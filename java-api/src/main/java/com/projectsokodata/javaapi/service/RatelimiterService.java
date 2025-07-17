package com.projectsokodata.javaapi.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class RateLimiterService {

    private final RedisTemplate<String, Object> redisTemplate;

    @Value("${rate.limiter.max-requests-per-minute:60}")
    private int maxRequestsPerMinute;
    
    @Value("${rate.limiter.window-size-minutes:1}")
    private int windowSizeMinutes;
    
    @Value("${rate.limiter.enabled:true}")
    private boolean enabled;

    public boolean isAllowed(String clientId) {
        if (!enabled) {
            return true;
        }
        
        try {
            String key = "rate_limit:" + clientId;

            // Get current count
            String currentCountStr = (String) redisTemplate.opsForValue().get(key);
            int currentCount = currentCountStr != null ? Integer.parseInt(currentCountStr) : 0;

            if (currentCount >= maxRequestsPerMinute) {
                log.warn("Rate limit exceeded for client: {} ({}/{})", 
                        clientId, currentCount, maxRequestsPerMinute);
                return false;
            }

            // Increment counter
            if (currentCount == 0) {
                // First request in window - set with expiration
                redisTemplate.opsForValue().set(key, "1", Duration.ofMinutes(windowSizeMinutes));
            } else {
                // Increment existing counter
                redisTemplate.opsForValue().increment(key);
            }

            log.debug("Client {} - Request count: {}/{}", 
                    clientId, currentCount + 1, maxRequestsPerMinute);
            return true;

        } catch (Exception e) {
            log.error("Error checking rate limit for client {}: {}", clientId, e.getMessage());
            // In case of Redis failure, allow the request (fail open)
            return true;
        }
    }

    public int getRemainingRequests(String clientId) {
        if (!enabled) {
            return maxRequestsPerMinute;
        }
        
        try {
            String key = "rate_limit:" + clientId;
            String currentCountStr = (String) redisTemplate.opsForValue().get(key);
            int currentCount = currentCountStr != null ? Integer.parseInt(currentCountStr) : 0;
            return Math.max(0, maxRequestsPerMinute - currentCount);
        } catch (Exception e) {
            log.error("Error getting remaining requests for client {}: {}", clientId, e.getMessage());
            return maxRequestsPerMinute;
        }
    }

    public long getWindowResetTime(String clientId) {
        try {
            String key = "rate_limit:" + clientId;
            return redisTemplate.getExpire(key, TimeUnit.SECONDS);
        } catch (Exception e) {
            log.error("Error getting reset time for client {}: {}", clientId, e.getMessage());
            return windowSizeMinutes * 60;
        }
    }
}