package com.fpl.server.controller;

import com.fpl.server.service.FplApiService;
import com.fpl.server.service.MLServiceClient;
import com.fpl.server.service.PlayerService;
import com.fpl.server.service.UserTeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/squads")
public class SquadController {

    @Autowired
    private PlayerService playerService;

    @Autowired
    private MLServiceClient mlServiceClient;

    @Autowired
    private UserTeamService userTeamService;

    @PostMapping("/optimize")
    public ResponseEntity<Map<String, Object>> optimizeSquad(@RequestBody Map<String, Object> request) {
        Double budget = 100.0;
        if (request.containsKey("budget")) {
            Object budgetObj = request.get("budget");
            if (budgetObj instanceof Number) {
                budget = ((Number) budgetObj).doubleValue();
            }
        }

        List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
        Map<String, Object> result = mlServiceClient.optimizeSquad(players, budget, true);

        return ResponseEntity.ok(result);
    }

    @GetMapping("/user/{fplId}")
    public ResponseEntity<Map<String, Object>> getUserSquad(@PathVariable String fplId) {
        Map<String, Object> result = userTeamService.getUserSquad(fplId);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/players")
    public ResponseEntity<List<Map<String, Object>>> getAllPlayers() {
        List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
        return ResponseEntity.ok(players);
    }
}
