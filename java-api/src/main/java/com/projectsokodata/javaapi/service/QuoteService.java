package com.projectsokodata.javaapi.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.projectsokodata.javaapi.model.Quote;
import org.springframework.data.redis.connection.stream.MapRecord;

import java.util.List;
import java.util.Optional;

import static java.util.stream.Collectors.toList;

@Service
@RequiredArgsConstructor
@Slf4j
public class QuoteService {
    private final RedisService redisService;

    private Quote fromRecord(MapRecord<String, Object, Object> rec) {
        try {
            var v = rec.getValue();
            log.debug("Processing record ID: {}, values: {}", rec.getId(), v);
            
            // Safely extract values as strings first
            String ticker = getStringValue(v, "ticker");
            String priceStr = getStringValue(v, "price");
            String tsStr = getStringValue(v, "ts");
            String priceChangeStr = getStringValue(v, "price_change");
            String priceChangeAbsStr = getStringValue(v, "price_change_abs");
            String direction = getStringValue(v, "price_change_direction");
            
            // Parse numeric values with error handling
            double price = parseDouble(priceStr, 0.0);
            long timestamp = parseLong(tsStr, System.currentTimeMillis());
            double priceChange = parseDouble(priceChangeStr, 0.0);
            double priceChangeAbs = parseDouble(priceChangeAbsStr, 0.0);
            
            Quote quote = new Quote(
                    rec.getId().getValue(),
                    ticker,
                    price,
                    timestamp,
                    priceChange,
                    priceChangeAbs,
                    direction
            );
            
            log.debug("Created quote: {}", quote);
            return quote;
        } catch (Exception e) {
            log.error("Error parsing record {}: {}", rec.getId(), e.getMessage());
            log.debug("Record content: {}", rec.getValue());
            
            // Return a default quote to prevent complete failure
            return new Quote(
                    rec.getId().getValue(),
                    "UNKNOWN",
                    0.0,
                    System.currentTimeMillis(),
                    0.0,
                    0.0,
                    "UNKNOWN"
            );
        }
    }
    
    private String getStringValue(java.util.Map<Object, Object> map, String key) {
        Object value = map.get(key);
        return value != null ? value.toString() : "";
    }
    
    private double parseDouble(String str, double defaultValue) {
        try {
            return str != null && !str.isEmpty() ? Double.parseDouble(str) : defaultValue;
        } catch (NumberFormatException e) {
            log.warn("Could not parse double value: {}", str);
            return defaultValue;
        }
    }
    
    private long parseLong(String str, long defaultValue) {
        try {
            return str != null && !str.isEmpty() ? Long.parseLong(str) : defaultValue;
        } catch (NumberFormatException e) {
            log.warn("Could not parse long value: {}", str);
            return defaultValue;
        }
    }

    public List<Quote> getLatest(int count, Optional<String> ticker, Optional<String> direction) {
        try {
            log.info("Getting latest {} quotes, ticker filter: {}, direction filter: {}", 
                    count, ticker.orElse("none"), direction.orElse("none"));
            
            var recs = redisService.readLatest("nse:realtime", count);
            log.info("Retrieved {} records from Redis stream", recs.size());
            
            if (recs.isEmpty()) {
                // Check if stream exists
                boolean exists = redisService.streamExists("nse:realtime");
                log.warn("No records found. Stream exists: {}", exists);
                
                if (!exists) {
                    log.warn("Stream 'nse:realtime' does not exist or is empty");
                    return List.of();
                }
            }
            
            List<Quote> quotes = recs.stream()
                    .map(this::fromRecord)
                    .filter(q -> ticker.map(t -> t.equalsIgnoreCase(q.ticker())).orElse(true))
                    .filter(q -> direction.map(d -> d.equalsIgnoreCase(q.priceChangeDirection())).orElse(true))
                    .collect(toList());
            
            log.info("Returning {} quotes after filtering", quotes.size());
            return quotes;
        } catch (Exception e) {
            log.error("Error getting latest quotes: {}", e.getMessage(), e);
            return List.of();
        }
    }

    public List<Quote> getHistory(String ticker, String fromId, int count) {
        try {
            log.info("Getting history for ticker: {}, fromId: {}, count: {}", ticker, fromId, count);
            
            var recs = redisService.readRange("nse:realtime", fromId, count);
            log.info("Retrieved {} records from Redis stream for history", recs.size());
            
            if (recs.isEmpty()) {
                boolean exists = redisService.streamExists("nse:realtime");
                log.warn("No records found for history. Stream exists: {}", exists);
            }
            
            List<Quote> quotes = recs.stream()
                    .map(this::fromRecord)
                    .filter(q -> ticker.equalsIgnoreCase(q.ticker()))
                    .collect(toList());
            
            log.info("Returning {} quotes for ticker {} after filtering", quotes.size(), ticker);
            return quotes;
        } catch (Exception e) {
            log.error("Error getting history for ticker {}: {}", ticker, e.getMessage(), e);
            return List.of();
        }
    }
}