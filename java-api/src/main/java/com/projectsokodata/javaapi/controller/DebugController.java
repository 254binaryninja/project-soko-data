package com.projectsokodata.javaapi.controller;

import com.projectsokodata.javaapi.service.RedisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Set;

@RestController
@RequestMapping("/api/v1/debug")
@RequiredArgsConstructor
@Slf4j
public class DebugController {
    
    private final RedisService redisService;
    
    @GetMapping("/redis-keys")
    public Set<String> getRedisKeys() {
        return redisService.getAllStreamKeys();
    }
    
    @GetMapping("/stream-info/{streamKey}")
    public Map<String, Object> getStreamInfo(@PathVariable String streamKey) {
        return redisService.getStreamInfo(streamKey);
    }
    
    @GetMapping("/stream-exists/{streamKey}")
    public Map<String, Object> streamExists(@PathVariable String streamKey) {
        boolean exists = redisService.streamExists(streamKey);
        return Map.of("streamKey", streamKey, "exists", exists);
    }
}