package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
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
        List<Map<String, Object>> fixtures = fplApiService.getFixtures();
        int currentGw = fplApiService.getCurrentGameweek();
        
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
        
        Map<Integer, List<Map<String, Object>>> teamFixtures = buildTeamFixtures(fixtures, teamMap, currentGw);
        
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
                    
                    List<Map<String, Object>> upcomingFixtures = teamFixtures.getOrDefault(teamId, new ArrayList<>());
                    // Return more fixtures to allow frontend to handle multi-gameweek planning
                    enriched.put("fixtures", upcomingFixtures.stream().limit(38).collect(Collectors.toList()));
                    
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
    
    private Map<Integer, List<Map<String, Object>>> buildTeamFixtures(
            List<Map<String, Object>> fixtures, 
            Map<Integer, String> teamMap,
            int currentGw) {
        
        Map<Integer, List<Map<String, Object>>> teamFixtures = new HashMap<>();
        
        List<Map<String, Object>> upcomingFixtures = fixtures.stream()
                .filter(f -> {
                    Object eventObj = f.get("event");
                    if (eventObj == null) return false;
                    int event = (Integer) eventObj;
                    return event >= currentGw;
                })
                .sorted(Comparator.comparingInt(f -> (Integer) f.get("event")))
                .collect(Collectors.toList());
        
        for (Map<String, Object> fixture : upcomingFixtures) {
            Integer homeTeam = (Integer) fixture.get("team_h");
            Integer awayTeam = (Integer) fixture.get("team_a");
            Integer homeTeamDifficulty = (Integer) fixture.get("team_h_difficulty");
            Integer awayTeamDifficulty = (Integer) fixture.get("team_a_difficulty");
            Integer event = (Integer) fixture.get("event");
            
            Map<String, Object> homeFixture = new HashMap<>();
            homeFixture.put("gw", event);
            homeFixture.put("opponent", teamMap.getOrDefault(awayTeam, "???"));
            homeFixture.put("opponent_id", awayTeam);
            homeFixture.put("is_home", true);
            homeFixture.put("fdr", homeTeamDifficulty);
            
            Map<String, Object> awayFixture = new HashMap<>();
            awayFixture.put("gw", event);
            awayFixture.put("opponent", teamMap.getOrDefault(homeTeam, "???"));
            awayFixture.put("opponent_id", homeTeam);
            awayFixture.put("is_home", false);
            awayFixture.put("fdr", awayTeamDifficulty);
            
            teamFixtures.computeIfAbsent(homeTeam, k -> new ArrayList<>()).add(homeFixture);
            teamFixtures.computeIfAbsent(awayTeam, k -> new ArrayList<>()).add(awayFixture);
        }
        
        return teamFixtures;
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
