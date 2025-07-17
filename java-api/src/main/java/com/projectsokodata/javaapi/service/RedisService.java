package com.projectsokodata.javaapi.service;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.connection.stream.*;
import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.time.Duration;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class RedisService {
    private final RedisTemplate<String, Object> redisTemplate;

    /** Reads latest N entries from the stream */
    public List<MapRecord<String, Object, Object>> readLatest(String streamKey, int count) {
        try {
            log.debug("Reading latest {} entries from stream: {}", count, streamKey);
            
            // Use ReadOffset.from("0") to read from beginning, then take last N
            StreamReadOptions options = StreamReadOptions.empty().count(count);
            StreamOffset<String> offset = StreamOffset.create(streamKey, ReadOffset.from("0"));
            
            List<MapRecord<String, Object, Object>> allRecords = read(streamKey, options, offset);
            
            log.debug("Read {} total records from stream {}", allRecords.size(), streamKey);
            
            // If we have more records than requested, take the last N
            if (allRecords.size() > count) {
                int startIndex = allRecords.size() - count;
                return allRecords.subList(startIndex, allRecords.size());
            }
            
            return allRecords;
        } catch (Exception e) {
            log.error("Error reading latest from stream {}: {}", streamKey, e.getMessage());
            return Collections.emptyList();
        }
    }

    /** Reads from a specific ID range */
    public List<MapRecord<String, Object, Object>> readRange(String streamKey, String fromId, int count) {
        try {
            log.debug("Reading {} entries from stream {} starting from ID: {}", count, streamKey, fromId);
            
            StreamReadOptions options = StreamReadOptions.empty().count(count);
            StreamOffset<String> offset = StreamOffset.create(streamKey, ReadOffset.from(fromId));
            
            List<MapRecord<String, Object, Object>> records = read(streamKey, options, offset);
            log.debug("Read {} records from stream {} starting from {}", records.size(), streamKey, fromId);
            
            return records;
        } catch (Exception e) {
            log.error("Error reading range from stream {} starting from {}: {}", streamKey, fromId, e.getMessage());
            return Collections.emptyList();
        }
    }

    private List<MapRecord<String, Object, Object>> read(
            String streamKey,
            StreamReadOptions options,
            StreamOffset<String> offset
    ) {
        try {
            // Check if stream exists first
            if (!streamExists(streamKey)) {
                log.warn("Stream {} does not exist or is empty", streamKey);
                return Collections.emptyList();
            }
            
            List<MapRecord<String, Object, Object>> records = redisTemplate.opsForStream().read(options, offset);
            log.debug("Successfully read {} records from stream {}", records != null ? records.size() : 0, streamKey);
            
            return records == null ? Collections.emptyList() : records;
        } catch (Exception e) {
            log.error("Error reading from stream {}: {}", streamKey, e.getMessage());
            return Collections.emptyList();
        }
    }

    /** Blocking read — awaits new messages after last ID */
    public List<MapRecord<String, Object, Object>> readBlocking(String streamKey, Duration timeout) {
        try {
            StreamReadOptions options = StreamReadOptions.empty().block(timeout);
            StreamOffset<String> offset = StreamOffset.create(streamKey, ReadOffset.latest());
            return read(streamKey, options, offset);
        } catch (Exception e) {
            log.error("Error in blocking read from stream {}: {}", streamKey, e.getMessage());
            return Collections.emptyList();
        }
    }
    
    /** Check if stream exists and has data */
    public boolean streamExists(String streamKey) {
        try {
            StreamInfo.XInfoStream info = redisTemplate.opsForStream().info(streamKey);
            boolean exists = info.streamLength() > 0;
            log.debug("Stream {} exists: {}, length: {}", streamKey, exists, info.streamLength());
            return exists;
        } catch (Exception e) {
            log.debug("Stream {} does not exist or is empty: {}", streamKey, e.getMessage());
            return false;
        }
    }
    
    /** Get all stream keys for debugging */
    public Set<String> getAllStreamKeys() {
        try {
            return redisTemplate.keys("*");
        } catch (Exception e) {
            log.error("Error getting Redis keys: {}", e.getMessage());
            return Collections.emptySet();
        }
    }
    
    /** Get stream information for debugging */
    public Map<String, Object> getStreamInfo(String streamKey) {
        try {
            StreamInfo.XInfoStream info = redisTemplate.opsForStream().info(streamKey);

            Map<String, Object> result = new HashMap<>();
            result.put("exists", true);
            result.put("length", info.streamLength());
            result.put("radixTreeKeys", info.radixTreeKeySize());
            result.put("radixTreeNodes", info.radixTreeNodesSize());
            result.put("groups", info.groupCount());
            result.put("lastGeneratedId", info.lastGeneratedId());
            
            // Handle first and last entries safely
            info.getFirstEntry();
            result.put("firstEntry", info.getFirstEntry().toString());
            info.getLastEntry();
            result.put("lastEntry", info.getLastEntry().toString());

            return result;
        } catch (Exception e) {
            return Map.of("exists", false, "error", e.getMessage());
        }
    }
}