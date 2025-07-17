package com.projectsokodata.javaapi.config;

import com.projectsokodata.javaapi.filter.RateLimiterFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
public class RateLimiterConfig {

    private final RateLimiterFilter rateLimiterFilter;

    @Bean
    public FilterRegistrationBean<RateLimiterFilter> rateLimiterFilterRegistration() {
        FilterRegistrationBean<RateLimiterFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(rateLimiterFilter);
        registration.addUrlPatterns("/api/*");
        registration.setOrder(1); // High priority
        registration.setName("rateLimiterFilter");
        return registration;
    }
}