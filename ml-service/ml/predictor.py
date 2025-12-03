"""
FPL Points Prediction Service - Hybrid Approach
================================================
This module combines:
1. Historical data from FPL-Elo-Insights (for rolling averages)
2. Live data from FPL API (for current form, price, ownership)

The hybrid approach gives us:
- Accurate rolling averages from actual gameweek data
- Real-time information from the official FPL API
"""

import numpy as np
import pandas as pd
import joblib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


# Paths
MODELS_PATH = Path(__file__).parent.parent / "models"
DATA_PATH = Path(__file__).parent.parent / "data"
ELO_INSIGHTS_PATH = DATA_PATH / "raw" / "FPL-Elo-Insights"


def update_dataset():
    """
    Pull latest updates from FPL-Elo-Insights GitHub repo.
    
    This fetches the latest gameweek data (updated twice daily at 5am/5pm UTC).
    Called on startup to ensure we have fresh data.
    """
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
    """
    FPL Points Predictor using Hybrid Approach.
    
    Combines:
    - Historical gameweek data (FPL-Elo-Insights) for accurate rolling stats
    - FPL API data for current form and ownership
    """
    
    def __init__(self, auto_update=True):
        """
        Initialize the predictor.
        
        Args:
            auto_update: Whether to pull latest data on startup
        """
        self.model = None
        self.player_history = {}  # player_id -> historical stats
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
        """Load the trained Linear Regression model."""
        model_path = MODELS_PATH / "linear_regression.pkl"
        
        if not model_path.exists():
            print(f"⚠ Model not found at {model_path}")
            print("  Run baseline_models.py first to train the model")
            self.model = None
            return
        
        self.model = joblib.load(model_path)
        print(f"✓ Loaded prediction model")
    
    def _load_player_history(self):
        """
        Load historical gameweek data and calculate rolling stats for each player.
        
        This creates a lookup table: player_id -> {last_6_avg_points, last_3_avg_points, etc.}
        """
        print("📊 Loading player historical data...")
        
        season = '2025-2026'
        gw_path = ELO_INSIGHTS_PATH / "data" / season / "By Gameweek"
        
        if not gw_path.exists():
            print(f"⚠ Gameweek data not found at {gw_path}")
            return
        
        # Load all gameweek data
        all_data = []
        import os
        gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
        
        for gw_folder in gw_folders:
            stats_file = gw_path / gw_folder / "player_gameweek_stats.csv"
            if stats_file.exists():
                df = pd.read_csv(stats_file)
                # The file already has 'gw' column, but let's ensure it exists
                if 'gw' not in df.columns:
                    df['gw'] = int(gw_folder.replace('GW', ''))
                all_data.append(df)
        
        if not all_data:
            print("⚠ No gameweek data found")
            return
        
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values(['id', 'gw'])
        
        print(f"  Loaded {len(combined)} records from GW1-{combined['gw'].max()}")
        
        # Calculate rolling stats for each player
        for player_id in combined['id'].unique():
            player_df = combined[combined['id'] == player_id].sort_values('gw')
            
            if len(player_df) == 0:
                continue
            
            # Get the most recent stats
            latest = player_df.iloc[-1]
            
            # Calculate rolling averages from actual gameweek data
            points = player_df['event_points'].values
            minutes = player_df['minutes'].values
            
            # Last 6 games average (or all games if less than 6)
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
        """
        Extract features for prediction using HYBRID approach.
        
        Priority:
        1. Rolling stats from FPL-Elo-Insights historical data (accurate)
        2. Live data from FPL API (form, price, ownership)
        
        Args:
            player: Player dict from FPL API
        
        Returns:
            numpy array of features
        """
        try:
            player_id = int(player.get('id', 0))
            
            # Get historical rolling stats (from our calculated data)
            history = self.player_history.get(player_id, {})
            
            # Historical features (from FPL-Elo-Insights)
            last_6_avg = history.get('last_6_avg_points', 2.0)
            last_3_avg = history.get('last_3_avg_points', 2.0)
            form_trend = history.get('form_trend', 0.0)
            last_6_avg_minutes = history.get('last_6_avg_minutes', 60.0)
            
            # Live features (from FPL API)
            form = float(player.get('form', 0) or 0)
            now_cost = float(player.get('now_cost', 50) or 50)
            selected_by = float(player.get('selected_by_percent', 0) or 0)
            
            # If no history (new player), estimate from FPL form
            if player_id not in self.player_history:
                last_6_avg = form * 0.9
                last_3_avg = form
                form_trend = 0.0
                last_6_avg_minutes = 60.0
            
            features = np.array([
                last_6_avg,           # From historical data
                last_3_avg,           # From historical data
                form_trend,           # From historical data
                last_6_avg_minutes,   # From historical data
                form,                 # From FPL API (live)
                now_cost,             # From FPL API (live)
                selected_by,          # From FPL API (live)
            ])
            
            return features
            
        except Exception as e:
            print(f"Error extracting features for player {player.get('id')}: {e}")
            return None
    
    def predict_single(self, player: Dict[str, Any]) -> float:
        """
        Predict points for a single player.
        
        Args:
            player: Dict with player data from FPL API
        
        Returns:
            Predicted points (float)
        """
        # Fallback if model not loaded
        if self.model is None:
            form = float(player.get('form', 0) or 0)
            return round(form * 1.2, 1)
        
        features = self._extract_features(player)
        
        if features is None:
            return 0.0
        
        # Make prediction
        prediction = self.model.predict([features])[0]
        
        # Clip to reasonable range
        prediction = np.clip(prediction, 0, 25)
        
        return round(float(prediction), 1)
    
    def predict_batch(self, players: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Predict points for multiple players.
        
        Args:
            players: List of player dicts from FPL API
        
        Returns:
            Dict mapping player_id (str) to predicted points (float)
        """
        predictions = {}
        
        for player in players:
            player_id = str(player.get('id', ''))
            if not player_id:
                continue
            
            predicted_points = self.predict_single(player)
            predictions[player_id] = predicted_points
        
        return predictions
    
    def get_player_stats(self, player_id: int) -> Dict:
        """
        Get calculated stats for a specific player.
        
        Useful for debugging and displaying player form.
        """
        return self.player_history.get(player_id, {})


# Global predictor instance
_predictor: Optional[FPLPredictor] = None


def get_predictor() -> FPLPredictor:
    """Get or create the global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = FPLPredictor(auto_update=True)
    return _predictor


def predict_players(players: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Public function to predict points for a list of players.
    
    This is the main entry point called by FastAPI.
    
    Args:
        players: List of player dicts from FPL API
    
    Returns:
        Dict mapping player_id to predicted points
    """
    predictor = get_predictor()
    return predictor.predict_batch(players)


if __name__ == '__main__':
    print("="*60)
    print("Testing FPL Predictor (Hybrid Approach)")
    print("="*60)
    
    # Initialize predictor
    predictor = FPLPredictor(auto_update=True)
    
    # Show some player stats from our data
    print("\n--- Sample Player Stats (from FPL-Elo-Insights) ---")
    sample_ids = list(predictor.player_history.keys())[:5]
    for pid in sample_ids:
        stats = predictor.player_history[pid]
        print(f"  ID {pid} ({stats.get('web_name', '?')}): "
              f"last_6_avg={stats['last_6_avg_points']:.1f}, "
              f"last_3_avg={stats['last_3_avg_points']:.1f}, "
              f"trend={stats['form_trend']:.2f}")
    
    # Test with mock FPL API data
    print("\n--- Test Predictions (with mock FPL API data) ---")
    sample_players = [
        {'id': 328, 'web_name': 'Salah', 'form': '8.5', 'now_cost': 130, 'selected_by_percent': '55.2'},
        {'id': 351, 'web_name': 'Haaland', 'form': '9.2', 'now_cost': 150, 'selected_by_percent': '78.1'},
        {'id': 6, 'web_name': 'Saka', 'form': '6.0', 'now_cost': 100, 'selected_by_percent': '42.3'},
    ]
    
    predictions = predictor.predict_batch(sample_players)
    
    for player in sample_players:
        pid = str(player['id'])
        hist = predictor.player_history.get(player['id'], {})
        print(f"  {player['web_name']}: {predictions.get(pid, 0):.1f} pts "
              f"(last_6_avg={hist.get('last_6_avg_points', 'N/A')})")
