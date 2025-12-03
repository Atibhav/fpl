package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class PlayerService {
    
    @Autowired
    private FplApiService fplApiService;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    public List<Map<String, Object>> getAllPlayersEnriched() {
        List<Map<String, Object>> players = fplApiService.getAllPlayers();
        List<Map<String, Object>> teams = fplApiService.getAllTeams();
        List<Map<String, Object>> elementTypes = fplApiService.getElementTypes();
        
        Map<Integer, String> teamMap = teams.stream()
                .collect(Collectors.toMap(
                        t -> (Integer) t.get("id"),
                        t -> (String) t.get("short_name")
                ));
        
        Map<Integer, String> positionMap = elementTypes.stream()
                .collect(Collectors.toMap(
                        e -> (Integer) e.get("id"),
                        e -> (String) e.get("singular_name_short")
                ));
        
        List<Map<String, Object>> enrichedPlayers = players.stream()
                .map(player -> {
                    Map<String, Object> enriched = new HashMap<>(player);
                    
                    Integer teamId = (Integer) player.get("team");
                    Integer positionId = (Integer) player.get("element_type");
                    
                    enriched.put("team_name", teamMap.getOrDefault(teamId, "Unknown"));
                    enriched.put("position", positionMap.getOrDefault(positionId, "Unknown"));
                    
                    Object nowCostObj = player.get("now_cost");
                    if (nowCostObj instanceof Integer) {
                        enriched.put("price", ((Integer) nowCostObj) / 10.0);
                    }
                    
                    String firstName = (String) player.get("first_name");
                    String secondName = (String) player.get("second_name");
                    enriched.put("full_name", firstName + " " + secondName);
                    
                    enriched.put("predicted_points", 0.0);
                    
                    return enriched;
                })
                .collect(Collectors.toList());
        
        try {
            Map<String, Double> predictions = mlServiceClient.getPredictions(players);
            
            if (!predictions.isEmpty()) {
                enrichedPlayers = enrichPlayersWithPredictions(enrichedPlayers, predictions);
                System.out.println("Successfully added predictions for " + predictions.size() + " players");
            } else {
                System.out.println("Warning: ML service returned empty predictions");
            }
        } catch (Exception e) {
            System.err.println("Warning: Could not get ML predictions: " + e.getMessage());
        }
        
        return enrichedPlayers;
    }
    
    public List<Map<String, Object>> enrichPlayersWithPredictions(
            List<Map<String, Object>> players,
            Map<String, Double> predictions) {
        
        return players.stream()
                .map(player -> {
                    Map<String, Object> enriched = new HashMap<>(player);
                    Object playerId = player.get("id");
                    String playerIdStr = String.valueOf(playerId);
                    enriched.put("predicted_points", predictions.getOrDefault(playerIdStr, 0.0));
                    return enriched;
                })
                .collect(Collectors.toList());
    }
}
