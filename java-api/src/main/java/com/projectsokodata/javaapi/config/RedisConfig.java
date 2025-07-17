package com.projectsokodata.javaapi.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import jakarta.annotation.PostConstruct;

@Configuration
@Slf4j
public class RedisConfig {
    
    private final RedisConnectionFactory redisConnectionFactory;

    public RedisConfig(RedisConnectionFactory redisConnectionFactory) {
        this.redisConnectionFactory = redisConnectionFactory;
    }

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // Use String serializer for Redis Streams compatibility
        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        
        // Set serializers for keys and values
        template.setKeySerializer(stringSerializer);
        template.setValueSerializer(stringSerializer);
        
        // Set serializers for hash keys and values
        template.setHashKeySerializer(stringSerializer);
        template.setHashValueSerializer(stringSerializer);
        
        // Set default serializer to String for stream compatibility
        template.setDefaultSerializer(stringSerializer);
        
        template.afterPropertiesSet();
        
        return template;
    }
    
    @PostConstruct
    public void testRedisConnection() {
        try {
            // Test Redis connection
            redisConnectionFactory.getConnection().ping();
            log.info("✅ Redis connection successful!");
            
            // Additional connection info
            var connection = redisConnectionFactory.getConnection();
            log.info("Redis server info: {}", connection.info());
            connection.close();
            
        } catch (Exception e) {
            log.error("❌ Redis connection failed: {}", e.getMessage());
            log.error("Please check your Redis server configuration and ensure it's running");
        }
    }
}