package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MLServiceClient {
    
    @Value("${ml.service.url}")
    private String mlServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    @SuppressWarnings("unchecked")
    public Map<String, Double> getPredictions(List<Map<String, Object>> players) {
        String url = mlServiceUrl + "/predict";
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("players", players);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            Map<String, Object> response = restTemplate.postForObject(url, request, Map.class);
            
            if (response != null && response.containsKey("predictions")) {
                Map<String, Object> predictions = (Map<String, Object>) response.get("predictions");
                
                Map<String, Double> result = new HashMap<>();
                for (Map.Entry<String, Object> entry : predictions.entrySet()) {
                    Object value = entry.getValue();
                    double points = 0.0;
                    if (value instanceof Number) {
                        points = ((Number) value).doubleValue();
                    }
                    result.put(entry.getKey(), points);
                }
                return result;
            }
            
            return new HashMap<>();
            
        } catch (Exception e) {
            System.err.println("ML Service error: " + e.getMessage());
            return new HashMap<>();
        }
    }
    
    @SuppressWarnings("unchecked")
    public Map<String, Object> optimizeSquad(List<Map<String, Object>> players, Double budget, boolean includeStartingEleven) {
        String url = mlServiceUrl + "/optimize/squad";
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("players", players);
            requestBody.put("budget", budget);
            requestBody.put("include_starting_eleven", includeStartingEleven);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            return restTemplate.postForObject(url, request, Map.class);
            
        } catch (Exception e) {
            throw new RuntimeException("Optimization failed: " + e.getMessage(), e);
        }
    }
    
    public boolean isHealthy() {
        String url = mlServiceUrl + "/health";
        
        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            return response != null && "ok".equals(response.get("status"));
        } catch (Exception e) {
            return false;
        }
    }
    
    @SuppressWarnings("unchecked")
    public Map<String, Object> getPlayerStats(int playerId) {
        String url = mlServiceUrl + "/player/" + playerId + "/stats";
        
        try {
            return restTemplate.getForObject(url, Map.class);
        } catch (Exception e) {
            System.err.println("Failed to get player stats: " + e.getMessage());
            return new HashMap<>();
        }
    }
}











