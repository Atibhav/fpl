"""
FPL ML Service - FastAPI Application

This is the main entry point for the ML microservice.
It handles:
1. Player points predictions using trained ML models
2. Squad optimization using PuLP linear programming

The Spring Boot backend calls this service internally.
Users never interact with this directly.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

# =============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# =============================================================================
# Pydantic models define the shape of data coming in and going out.
# FastAPI uses these for:
# 1. Automatic validation (wrong types = 422 error)
# 2. Auto-generated API documentation
# 3. IDE autocomplete support

class PlayerFeatures(BaseModel):
    """Features for a single player prediction"""
    id: int
    name: str
    position: str  # GK, DEF, MID, FWD
    team: str
    price: float
    form: Optional[float] = 0.0
    total_points: Optional[int] = 0
    minutes: Optional[int] = 0
    goals_scored: Optional[int] = 0
    assists: Optional[int] = 0
    clean_sheets: Optional[int] = 0


class PredictionRequest(BaseModel):
    """Request body for /predict endpoint"""
    players: List[PlayerFeatures]


class PredictionResponse(BaseModel):
    """Response from /predict endpoint"""
    predictions: Dict[str, float]  # {player_id: predicted_points}


class OptimizeRequest(BaseModel):
    """Request body for /optimize/squad endpoint"""
    players: List[Dict]  # Players with predicted_points
    budget: float = 100.0


class OptimizeResponse(BaseModel):
    """Response from /optimize/squad endpoint"""
    squad: List[Dict]
    total_cost: float
    expected_points: float
    status: str


class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str
    message: str
    version: str


# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="FPL ML Service",
    description="Machine Learning predictions and squad optimization for Fantasy Premier League",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI at /docs
    redoc_url="/redoc"     # ReDoc at /redoc
)

# CORS Configuration
# Allows Spring Boot backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your backend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint.
    
    Used by:
    - Spring Boot to verify ML service is running
    - Render.com for health monitoring
    - Manual testing
    """
    return HealthResponse(
        status="ok",
        message="FPL ML Service is running!",
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
def predict_points(request: PredictionRequest):
    """
    Predict points for a list of players.
    
    This endpoint:
    1. Receives player data from Spring Boot
    2. Extracts features for each player
    3. Runs predictions through trained ML models
    4. Returns predicted points per player
    
    For now, returns dummy predictions (form * 1.5).
    Will be replaced with actual ML model predictions.
    """
    predictions = {}
    
    for player in request.players:
        # PLACEHOLDER: Simple prediction based on form
        # TODO: Replace with actual ML model prediction
        predicted = float(player.form) * 1.5 if player.form else 2.0
        predictions[str(player.id)] = round(predicted, 1)
    
    return PredictionResponse(predictions=predictions)


@app.post("/optimize/squad", response_model=OptimizeResponse)
def optimize_squad(request: OptimizeRequest):
    """
    Optimize squad selection using Linear Programming.
    
    This endpoint:
    1. Receives all players with predicted points
    2. Uses PuLP to solve the optimization problem
    3. Returns the optimal 15-player squad
    
    Constraints:
    - Exactly 15 players
    - Budget limit (default £100m)
    - 2 GK, 5 DEF, 5 MID, 3 FWD
    - Max 3 players per team
    
    For now, returns a simple sorted selection.
    TODO: Implement full PuLP optimization.
    """
    players = request.players
    budget = request.budget
    
    # PLACEHOLDER: Simple selection (top players by predicted points)
    # TODO: Replace with PuLP optimization
    
    # Sort by predicted points (descending)
    sorted_players = sorted(
        players, 
        key=lambda x: x.get('predicted_points', 0), 
        reverse=True
    )
    
    # Simple greedy selection (not optimal, just placeholder)
    selected = []
    total_cost = 0.0
    position_counts = {'GK': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}
    position_limits = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
    team_counts = {}
    
    for player in sorted_players:
        pos = player.get('position', 'MID')
        team = player.get('team', 'Unknown')
        price = player.get('price', 0)
        
        # Check constraints
        if len(selected) >= 15:
            break
        if position_counts.get(pos, 0) >= position_limits.get(pos, 0):
            continue
        if team_counts.get(team, 0) >= 3:
            continue
        if total_cost + price > budget:
            continue
        
        # Add player
        selected.append(player)
        total_cost += price
        position_counts[pos] = position_counts.get(pos, 0) + 1
        team_counts[team] = team_counts.get(team, 0) + 1
    
    expected_points = sum(p.get('predicted_points', 0) for p in selected)
    
    return OptimizeResponse(
        squad=selected,
        total_cost=round(total_cost, 1),
        expected_points=round(expected_points, 1),
        status="Optimal" if len(selected) == 15 else "Partial"
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run with: python main.py
    # Or: uvicorn main:app --reload --port 5001
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True  # Auto-reload on code changes (dev only)
    )

