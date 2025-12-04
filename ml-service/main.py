from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn

from ml.predictor import predict_players, get_predictor
from optimization.team_optimizer import optimize_squad, optimize_with_starting_eleven


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
    include_starting_eleven: bool = False


class OptimizeResponse(BaseModel):
    squad: List[Dict]
    total_cost: float
    expected_points: float
    status: str
    budget_remaining: Optional[float] = None
    starters: Optional[List[Dict]] = None
    bench: Optional[List[Dict]] = None
    formation: Optional[str] = None
    starting_expected_points: Optional[float] = None


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
def optimize_squad_endpoint(request: OptimizeRequest):
    try:
        if request.include_starting_eleven:
            result = optimize_with_starting_eleven(request.players, request.budget)
        else:
            result = optimize_squad(request.players, request.budget)
        
        return OptimizeResponse(
            squad=result.get('squad', []),
            total_cost=result.get('total_cost', 0.0),
            expected_points=result.get('expected_points', 0.0),
            status=result.get('status', 'Unknown'),
            budget_remaining=result.get('budget_remaining'),
            starters=result.get('starters'),
            bench=result.get('bench'),
            formation=result.get('formation'),
            starting_expected_points=result.get('starting_expected_points')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )
