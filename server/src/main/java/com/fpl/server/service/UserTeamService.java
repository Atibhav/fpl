package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class UserTeamService {

    @Autowired
    private FplApiService fplApiService;

    @Autowired
    private PlayerService playerService;

    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserSquad(String fplId) {
        Map<String, Object> result = new HashMap<>();

        try {
            Map<String, Object> userInfo = fplApiService.getUserTeam(fplId);
            int currentGw = fplApiService.getCurrentGameweek();
            Map<String, Object> picks = fplApiService.getUserPicks(fplId, currentGw);

            String teamName = (String) userInfo.get("name");
            String managerName = (String) userInfo.get("player_first_name") + " " + userInfo.get("player_last_name");

            Map<String, Object> currentEvent = (Map<String, Object>) picks.get("entry_history");
            Double bank = currentEvent != null ? ((Number) currentEvent.get("bank")).doubleValue() / 10.0 : 0.0;
            Integer freeTransfers = currentEvent != null ? (Integer) currentEvent.get("event_transfers") : 1;
            
            Map<String, Object> history = fplApiService.getUserHistory(fplId);
            List<Map<String, Object>> currentSeasonHistory = (List<Map<String, Object>>) history.get("current");
            
            int availableTransfers = 1;
            if (currentSeasonHistory != null && !currentSeasonHistory.isEmpty()) {
                Map<String, Object> lastGw = currentSeasonHistory.get(currentSeasonHistory.size() - 1);
                Integer gwTransfers = (Integer) lastGw.get("event_transfers");
                Integer gwTransfersCost = (Integer) lastGw.get("event_transfers_cost");
                
                if (gwTransfersCost != null && gwTransfersCost == 0 && gwTransfers != null && gwTransfers == 0) {
                    availableTransfers = 2;
                }
            }

            List<Map<String, Object>> picksList = (List<Map<String, Object>>) picks.get("picks");
            List<Map<String, Object>> allPlayers = playerService.getAllPlayersEnriched();

            Map<Integer, Map<String, Object>> playerMap = allPlayers.stream()
                    .collect(Collectors.toMap(
                            p -> (Integer) p.get("id"),
                            p -> p
                    ));

            List<Map<String, Object>> squad = new ArrayList<>();
            List<Map<String, Object>> starters = new ArrayList<>();
            List<Map<String, Object>> bench = new ArrayList<>();

            for (Map<String, Object> pick : picksList) {
                Integer playerId = (Integer) pick.get("element");
                Integer position = (Integer) pick.get("position");
                Boolean isCaptain = (Boolean) pick.get("is_captain");
                Boolean isViceCaptain = (Boolean) pick.get("is_vice_captain");

                Map<String, Object> playerData = playerMap.get(playerId);
                if (playerData != null) {
                    Map<String, Object> squadPlayer = new HashMap<>(playerData);
                    squadPlayer.put("squad_position", position);
                    squadPlayer.put("is_captain", isCaptain);
                    squadPlayer.put("is_vice_captain", isViceCaptain);
                    squadPlayer.put("is_starter", position <= 11);

                    squad.add(squadPlayer);

                    if (position <= 11) {
                        starters.add(squadPlayer);
                    } else {
                        bench.add(squadPlayer);
                    }
                }
            }

            starters.sort(Comparator.comparing(p -> (Integer) p.get("squad_position")));
            bench.sort(Comparator.comparing(p -> (Integer) p.get("squad_position")));

            Double totalValue = squad.stream()
                    .mapToDouble(p -> ((Number) p.getOrDefault("price", 0)).doubleValue())
                    .sum();

            result.put("fpl_id", fplId);
            result.put("team_name", teamName);
            result.put("manager_name", managerName);
            result.put("gameweek", currentGw);
            result.put("bank", bank);
            result.put("free_transfers", availableTransfers);
            result.put("squad_value", Math.round(totalValue * 10) / 10.0);
            result.put("squad", squad);
            result.put("starters", starters);
            result.put("bench", bench);
            result.put("status", "success");

        } catch (Exception e) {
            result.put("status", "error");
            result.put("message", "Failed to load team: " + e.getMessage());
        }

        return result;
    }
}

