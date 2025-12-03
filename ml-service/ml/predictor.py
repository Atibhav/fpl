"""
Prediction Service

This module loads trained ML models and provides predictions.
Currently a placeholder - will be implemented after training models.
"""

def predict_player_points(player_features: dict) -> float:
    """
    Predict points for a single player.
    
    Args:
        player_features: Dict with player stats (form, minutes, goals, etc.)
    
    Returns:
        Predicted points (float)
    
    TODO: Load actual trained models and make real predictions
    """
    # Placeholder: Simple heuristic based on form
    form = player_features.get('form', 0)
    return float(form) * 1.5 if form else 2.0


def predict_all_players(players: list) -> dict:
    """
    Predict points for all players.
    
    Args:
        players: List of player dicts
    
    Returns:
        Dict mapping player_id -> predicted_points
    """
    predictions = {}
    for player in players:
        player_id = player.get('id')
        predicted = predict_player_points(player)
        predictions[str(player_id)] = round(predicted, 1)
    return predictions

