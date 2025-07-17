package com.projectsokodata.javaapi.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.projectsokodata.javaapi.service.RateLimiterService;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class RateLimiterFilter implements Filter {
    
    private final RateLimiterService rateLimiterService;
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Value("${rate.limiter.max-requests-per-minute:60}")
    private int maxRequestsPerMinute;
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        
        String clientId = getClientId(httpRequest);
        
        if (!rateLimiterService.isAllowed(clientId)) {
            handleRateLimitExceeded(httpResponse, clientId);
            return;
        }
        
        // Add rate limit headers
        addRateLimitHeaders(httpResponse, clientId);
        
        chain.doFilter(request, response);
    }
    
    private String getClientId(HttpServletRequest request) {
        // Try to get client ID from various sources
        String clientId = request.getHeader("X-Client-ID");
        if (clientId != null && !clientId.isEmpty()) {
            return clientId;
        }
        
        // Fall back to IP address
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        return request.getRemoteAddr();
    }
    
    private void handleRateLimitExceeded(HttpServletResponse response, String clientId) 
            throws IOException {
        
        response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
        response.setContentType("application/json");
        
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("error", "Rate limit exceeded");
        errorResponse.put("message", "Too many requests. Please try again later.");
        errorResponse.put("status", HttpStatus.TOO_MANY_REQUESTS.value());
        
        long resetTime = rateLimiterService.getWindowResetTime(clientId);
        errorResponse.put("retryAfter", resetTime);
        
        // Add rate limit headers
        addRateLimitHeaders(response, clientId);
        response.setHeader("Retry-After", String.valueOf(resetTime));
        
        response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
        
        log.warn("Rate limit exceeded for client: {}", clientId);
    }
    
    private void addRateLimitHeaders(HttpServletResponse response, String clientId) {
        int remaining = rateLimiterService.getRemainingRequests(clientId);
        long resetTime = rateLimiterService.getWindowResetTime(clientId);
        
        response.setHeader("X-RateLimit-Limit", String.valueOf(maxRequestsPerMinute));
        response.setHeader("X-RateLimit-Remaining", String.valueOf(remaining));
        response.setHeader("X-RateLimit-Reset", String.valueOf(System.currentTimeMillis() / 1000 + resetTime));
    }
}