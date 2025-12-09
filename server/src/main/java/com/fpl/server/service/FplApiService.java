package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class FplApiService {
    
    @Value("${fpl.api.base-url}")
    private String fplBaseUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
    private static final long CACHE_DURATION_MS = 5 * 60 * 1000;
    
    private static class CacheEntry {
        Object data;
        long timestamp;
        
        CacheEntry(Object data) {
            this.data = data;
            this.timestamp = System.currentTimeMillis();
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() - timestamp > CACHE_DURATION_MS;
        }
    }
    
    @SuppressWarnings("unchecked")
    public Map<String, Object> getBootstrapData() {
        String cacheKey = "bootstrap";
        
        CacheEntry entry = cache.get(cacheKey);
        if (entry != null && !entry.isExpired()) {
            return (Map<String, Object>) entry.data;
        }
        
        String url = fplBaseUrl + "/bootstrap-static/";
        Map<String, Object> response = restTemplate.getForObject(url, Map.class);
        
        if (response != null) {
            cache.put(cacheKey, new CacheEntry(response));
        }
        
        return response;
    }
    
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getAllPlayers() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("elements");
    }
    
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getAllTeams() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("teams");
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getGameweeks() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("events");
    }
    
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getElementTypes() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("element_types");
    }
    
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getFixtures() {
        String cacheKey = "fixtures";
        
        CacheEntry entry = cache.get(cacheKey);
        if (entry != null && !entry.isExpired()) {
            return (List<Map<String, Object>>) entry.data;
        }
        
        String url = fplBaseUrl + "/fixtures/";
        List<Map<String, Object>> response = restTemplate.getForObject(url, List.class);
        
        if (response != null) {
            cache.put(cacheKey, new CacheEntry(response));
        }
        
        return response;
    }
    
    public Map<String, Object> getUserTeam(String fplId) {
        String url = fplBaseUrl + "/entry/" + fplId + "/";
        return restTemplate.getForObject(url, Map.class);
    }
    
    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserPicks(String fplId, int gameweek) {
        String url = fplBaseUrl + "/entry/" + fplId + "/event/" + gameweek + "/picks/";
        return restTemplate.getForObject(url, Map.class);
    }
    
    @SuppressWarnings("unchecked")
    public int getCurrentGameweek() {
        Map<String, Object> bootstrap = getBootstrapData();
        List<Map<String, Object>> events = (List<Map<String, Object>>) bootstrap.get("events");
        
        return events.stream()
                .filter(event -> Boolean.TRUE.equals(event.get("is_current")))
                .findFirst()
                .map(event -> (Integer) event.get("id"))
                .orElse(1);
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getUserTransfers(String fplId) {
        String url = fplBaseUrl + "/entry/" + fplId + "/transfers/";
        return restTemplate.getForObject(url, List.class);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserHistory(String fplId) {
        String url = fplBaseUrl + "/entry/" + fplId + "/history/";
        return restTemplate.getForObject(url, Map.class);
    }
}

