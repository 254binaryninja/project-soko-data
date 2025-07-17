package com.projectsokodata.javaapi.model;

public record Quote(
        String id,
        String ticker,
        double price,
        long ts,
        double priceChange,
        double priceChangeAbs,
        String priceChangeDirection
) { }
