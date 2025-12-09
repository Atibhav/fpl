package com.fpl.server.controller;

import com.fpl.server.service.FplApiService;
import com.fpl.server.service.PlayerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/players")
public class PlayerController {
    
    @Autowired
    private FplApiService fplApiService;
    
    @Autowired
    private PlayerService playerService;
    
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getAllPlayers() {
        try {
            List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
            return ResponseEntity.ok(players);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getPlayer(@PathVariable Integer id) {
        try {
            List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
            
            return players.stream()
                    .filter(p -> id.equals(p.get("id")))
                    .findFirst()
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/teams")
    public ResponseEntity<List<Map<String, Object>>> getAllTeams() {
        try {
            List<Map<String, Object>> teams = fplApiService.getAllTeams();
            return ResponseEntity.ok(teams);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/gameweeks")
    public ResponseEntity<List<Map<String, Object>>> getGameweeks() {
        try {
            List<Map<String, Object>> gameweeks = fplApiService.getGameweeks();
            return ResponseEntity.ok(gameweeks);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/fixtures")
    public ResponseEntity<List<Map<String, Object>>> getFixtures() {
        try {
            List<Map<String, Object>> fixtures = fplApiService.getFixtures();
            return ResponseEntity.ok(fixtures);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/gameweek/current")
    public ResponseEntity<Map<String, Object>> getCurrentGameweek() {
        try {
            int gw = fplApiService.getCurrentGameweek();
            return ResponseEntity.ok(Map.of("current_gameweek", gw));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}

