package com.projectsokodata.javaapi.controller;

import com.projectsokodata.javaapi.model.Quote;
import com.projectsokodata.javaapi.service.QuoteService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/quotes")
@RequiredArgsConstructor
public class QuoteController {
    private final QuoteService quoteService;

    @GetMapping
    public List<Quote> latest(
            @RequestParam(defaultValue = "100") int count,
            @RequestParam Optional<String> ticker,
            @RequestParam Optional<String> direction
    ) {
        return quoteService.getLatest(count, ticker, direction);
    }

    @GetMapping("/history")
    public List<Quote> history(
            @RequestParam String ticker,
            @RequestParam String fromId,
            @RequestParam int count
    ) {
        return quoteService.getHistory(ticker, fromId, count);
    }
}
