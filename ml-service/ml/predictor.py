import numpy as np
import pandas as pd
import joblib
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


MODELS_PATH = Path(__file__).parent.parent / "models"
DATA_PATH = Path(__file__).parent.parent / "data"
ELO_INSIGHTS_PATH = DATA_PATH / "raw" / "FPL-Elo-Insights"


def update_dataset():
    if not ELO_INSIGHTS_PATH.exists():
        print("⚠ FPL-Elo-Insights not found. Please clone it first:")
        print(f"  cd {DATA_PATH / 'raw'}")
        print("  git clone https://github.com/olbauday/FPL-Elo-Insights.git")
        return False
    
    try:
        print("📥 Checking for FPL-Elo-Insights updates...")
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=ELO_INSIGHTS_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "Already up to date" in result.stdout:
            print("✓ Data is already up to date")
        else:
            print("✓ Data updated successfully")
            print(result.stdout)
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠ Git pull timed out, using existing data")
        return True
    except Exception as e:
        print(f"⚠ Could not update data: {e}")
        print("  Using existing data")
        return True


class FPLPredictor:
    
    def __init__(self, auto_update=True):
        self.model = None
        self.player_history = {}
        self.feature_columns = [
            'last_6_avg_points',
            'last_3_avg_points',
            'form_trend',
            'last_6_avg_minutes',
            'form',
            'now_cost',
            'selected_by_percent',
        ]
        
        if auto_update:
            update_dataset()
        
        self._load_model()
        self._load_player_history()
    
    def _load_model(self):
        model_path = MODELS_PATH / "linear_regression.pkl"
        
        if not model_path.exists():
            print(f"⚠ Model not found at {model_path}")
            print("  Run baseline_models.py first to train the model")
            self.model = None
            return
        
        self.model = joblib.load(model_path)
        print(f"✓ Loaded prediction model")
    
    def _load_player_history(self):
        print("📊 Loading player historical data...")
        
        season = '2025-2026'
        gw_path = ELO_INSIGHTS_PATH / "data" / season / "By Gameweek"
        
        if not gw_path.exists():
            print(f"⚠ Gameweek data not found at {gw_path}")
            return
        
        all_data = []
        gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
        
        for gw_folder in gw_folders:
            stats_file = gw_path / gw_folder / "player_gameweek_stats.csv"
            if stats_file.exists():
                df = pd.read_csv(stats_file)
                if 'gw' not in df.columns:
                    df['gw'] = int(gw_folder.replace('GW', ''))
                all_data.append(df)
        
        if not all_data:
            print("⚠ No gameweek data found")
            return
        
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values(['id', 'gw'])
        
        print(f"  Loaded {len(combined)} records from GW1-{combined['gw'].max()}")
        
        for player_id in combined['id'].unique():
            player_df = combined[combined['id'] == player_id].sort_values('gw')
            
            if len(player_df) == 0:
                continue
            
            latest = player_df.iloc[-1]
            points = player_df['event_points'].values
            minutes = player_df['minutes'].values
            
            last_6_points = points[-6:] if len(points) >= 1 else [2.0]
            last_3_points = points[-3:] if len(points) >= 1 else [2.0]
            last_6_minutes = minutes[-6:] if len(minutes) >= 1 else [60.0]
            
            self.player_history[int(player_id)] = {
                'last_6_avg_points': float(np.mean(last_6_points)),
                'last_3_avg_points': float(np.mean(last_3_points)),
                'form_trend': float(np.mean(last_3_points) - np.mean(last_6_points)),
                'last_6_avg_minutes': float(np.mean(last_6_minutes)),
                'games_played': len(player_df),
                'total_points': int(points.sum()),
                'web_name': latest.get('web_name', ''),
            }
        
        print(f"✓ Calculated rolling stats for {len(self.player_history)} players")
    
    def _extract_features(self, player: Dict[str, Any]) -> Optional[np.ndarray]:
        try:
            player_id = player.get('id')
            if player_id is None:
                return None
            
            player_id = int(player_id)
            history = self.player_history.get(player_id, {})
            
            last_6_avg = history.get('last_6_avg_points', 2.0)
            last_3_avg = history.get('last_3_avg_points', 2.0)
            form_trend = history.get('form_trend', 0.0)
            last_6_avg_minutes = history.get('last_6_avg_minutes', 60.0)
            
            form = float(player.get('form', 0) or 0)
            now_cost = float(player.get('now_cost', 50) or 50)
            selected_by = float(player.get('selected_by_percent', 0) or 0)
            
            if player_id not in self.player_history:
                last_6_avg = form * 0.9
                last_3_avg = form
                form_trend = 0.0
                last_6_avg_minutes = 60.0
            
            features = np.array([
                last_6_avg,
                last_3_avg,
                form_trend,
                last_6_avg_minutes,
                form,
                now_cost,
                selected_by,
            ])
            
            return features
            
        except Exception as e:
            print(f"Error extracting features for player {player.get('id')}: {e}")
            return None
    
    def predict_single(self, player: Dict[str, Any]) -> float:
        if self.model is None:
            form = float(player.get('form', 0) or 0)
            return round(form * 1.2, 1)
        
        features = self._extract_features(player)
        
        if features is None:
            return 0.0
        
        prediction = self.model.predict([features])[0]
        prediction = np.clip(prediction, 0, 25)
        
        return round(float(prediction), 1)
    
    def predict_batch(self, players: List[Dict[str, Any]]) -> Dict[str, float]:
        predictions = {}
        
        for player in players:
            player_id = player.get('id')
            
            if player_id is None:
                continue
            
            player_id_str = str(player_id)
            if not player_id_str or player_id_str == 'None':
                continue
            
            predicted_points = self.predict_single(player)
            predictions[player_id_str] = predicted_points
        
        return predictions
    
    def get_player_stats(self, player_id: int) -> Dict:
        return self.player_history.get(player_id, {})


_predictor: Optional[FPLPredictor] = None


def get_predictor() -> FPLPredictor:
    global _predictor
    if _predictor is None:
        _predictor = FPLPredictor(auto_update=True)
    return _predictor


def predict_players(players: List[Dict[str, Any]]) -> Dict[str, float]:
    predictor = get_predictor()
    return predictor.predict_batch(players)
