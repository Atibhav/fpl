from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn

from ml.predictor import predict_players, get_predictor


class PlayerFeatures(BaseModel):
    id: int
    name: str
    position: str
    team: str
    price: float
    form: Optional[float] = 0.0
    total_points: Optional[int] = 0
    minutes: Optional[int] = 0
    goals_scored: Optional[int] = 0
    assists: Optional[int] = 0
    clean_sheets: Optional[int] = 0


class PredictionRequest(BaseModel):
    players: List[Dict[str, Any]]


class PredictionResponse(BaseModel):
    predictions: Dict[str, float]


class OptimizeRequest(BaseModel):
    players: List[Dict]
    budget: float = 100.0


class OptimizeResponse(BaseModel):
    squad: List[Dict]
    total_cost: float
    expected_points: float
    status: str


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


app = FastAPI(
    title="FPL ML Service",
    description="Machine Learning predictions and squad optimization for Fantasy Premier League",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("🚀 Starting FPL ML Service...")
    predictor = get_predictor()
    print(f"✓ Service ready with {len(predictor.player_history)} players loaded")


@app.get("/health", response_model=HealthResponse)
def health_check():
    predictor = get_predictor()
    player_count = len(predictor.player_history)
    model_loaded = predictor.model is not None
    
    return HealthResponse(
        status="ok",
        message=f"FPL ML Service running! Model: {'loaded' if model_loaded else 'not loaded'}, Players: {player_count}",
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
def predict_points(request: PredictionRequest):
    try:
        predictions = predict_players(request.players)
        return PredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/player/{player_id}/stats")
def get_player_stats(player_id: int):
    predictor = get_predictor()
    stats = predictor.get_player_stats(player_id)
    
    if not stats:
        raise HTTPException(
            status_code=404, 
            detail=f"Player {player_id} not found in historical data"
        )
    
    return {
        "player_id": player_id,
        "stats": stats
    }


@app.post("/optimize/squad", response_model=OptimizeResponse)
def optimize_squad(request: OptimizeRequest):
    players = request.players
    budget = request.budget
    
    sorted_players = sorted(
        players, 
        key=lambda x: x.get('predicted_points', 0), 
        reverse=True
    )
    
    selected = []
    total_cost = 0.0
    position_counts = {'GK': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}
    position_limits = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
    team_counts = {}
    
    for player in sorted_players:
        pos = player.get('position', 'MID')
        team = player.get('team', 'Unknown')
        price = player.get('price', 0)
        
        if len(selected) >= 15:
            break
        if position_counts.get(pos, 0) >= position_limits.get(pos, 0):
            continue
        if team_counts.get(team, 0) >= 3:
            continue
        if total_cost + price > budget:
            continue
        
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )
