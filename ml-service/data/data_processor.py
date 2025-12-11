"""
FPL Data Processor - FPL-Elo-Insights Dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os


# Path to the FPL-Elo-Insights data directory
DATA_PATH = Path(__file__).parent / "raw" / "FPL-Elo-Insights" / "data"


def load_teams_with_elo(season='2025-2026'):
    """
    Load team data including Elo ratings.
    
    Returns:
        pd.DataFrame: Teams with Elo and strength ratings
    """
    # Handle different folder structures between seasons
    teams_path = DATA_PATH / season / "teams.csv"
    if not teams_path.exists():
        teams_path = DATA_PATH / season / "teams" / "teams.csv"
    
    if not teams_path.exists():
        print(f"  Warning: teams.csv not found for {season}")
        return pd.DataFrame()
    
    teams = pd.read_csv(teams_path)
    
    print(f"  Loaded {len(teams)} teams from {season}")
    if 'elo' in teams.columns:
        print(f"  Elo range: {teams['elo'].min():.0f} - {teams['elo'].max():.0f}")
    
    return teams


def load_player_gameweek_stats(season='2025-2026', max_gw=None):
    """
    Load per-gameweek discrete player stats.
    
    Args:
        season: Season folder name (e.g., '2025-2026')
        max_gw: Maximum gameweek to load (None = all available)
    
    Returns:
        pd.DataFrame: Per-gameweek player stats
    """
    gw_path = DATA_PATH / season / "By Gameweek"
    
    all_gw_data = []
    gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
    
    for gw_folder in gw_folders:
        gw_num = int(gw_folder.replace('GW', ''))
        
        if max_gw and gw_num > max_gw:
            continue
        
        stats_file = gw_path / gw_folder / "player_gameweek_stats.csv"
        
        if stats_file.exists():
            gw_df = pd.read_csv(stats_file)
            gw_df['gw'] = gw_num
            gw_df['season'] = season
            all_gw_data.append(gw_df)
    
    if not all_gw_data:
        print(f"  Warning: No gameweek data found for {season}")
        return pd.DataFrame()
    
    combined = pd.concat(all_gw_data, ignore_index=True)
    print(f"  Loaded {len(combined)} player-gameweek records from {season}")
    print(f"  Gameweeks: {combined['gw'].min()} to {combined['gw'].max()}")
    
    return combined


def load_matches_with_team_xg(season='2025-2026'):
    """
    Load match data with team-level xG and Elo.
    
    Each match has:
    - home_team_elo, away_team_elo
    - home_expected_goals_xg, away_expected_goals_xg
    - Full match stats (possession, shots, etc.)
    
    Returns:
        pd.DataFrame: Match data with team xG and Elo
    """
    gw_path = DATA_PATH / season / "By Gameweek"
    
    all_matches = []
    gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
    
    for gw_folder in gw_folders:
        gw_num = int(gw_folder.replace('GW', ''))
        matches_file = gw_path / gw_folder / "matches.csv"
        
        if matches_file.exists():
            matches_df = pd.read_csv(matches_file)
            matches_df['season'] = season
            all_matches.append(matches_df)
    
    if not all_matches:
        return pd.DataFrame()
    
    combined = pd.concat(all_matches, ignore_index=True)
    print(f"  Loaded {len(combined)} matches from {season}")
    
    return combined


def load_player_match_stats(season='2025-2026'):
    """
    Load detailed per-match player stats (Opta-like).
    
    Includes:
    - xg, xa per match
    - CBIT: tackles_won, interceptions, blocks, clearances
    - Detailed passing, shooting, dribbling stats
    
    Returns:
        pd.DataFrame: Detailed player match stats
    """
    gw_path = DATA_PATH / season / "By Gameweek"
    
    all_stats = []
    gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
    
    for gw_folder in gw_folders:
        gw_num = int(gw_folder.replace('GW', ''))
        stats_file = gw_path / gw_folder / "playermatchstats.csv"
        
        if stats_file.exists():
            stats_df = pd.read_csv(stats_file)
            stats_df['gw'] = gw_num
            stats_df['season'] = season
            all_stats.append(stats_df)
    
    if not all_stats:
        return pd.DataFrame()
    
    combined = pd.concat(all_stats, ignore_index=True)
    print(f"  Loaded {len(combined)} player-match records from {season}")
    
    return combined


def load_players(season='2025-2026'):
    """
    Load player basic info (id, name, position, team).
    
    Returns:
        pd.DataFrame: Player info
    """
    # Handle different folder structures between seasons
    players_path = DATA_PATH / season / "players.csv"
    if not players_path.exists():
        players_path = DATA_PATH / season / "players" / "players.csv"
    
    if not players_path.exists():
        print(f"  Warning: players.csv not found for {season}")
        return pd.DataFrame()
    
    players = pd.read_csv(players_path)
    
    print(f"  Loaded {len(players)} players from {season}")
    
    return players


def calculate_team_stats(matches_df, teams_df):
    """
    Calculate aggregated team stats from matches.
    
    For each team, calculates:
    - avg_xg_for: Average xG scored per game
    - avg_xg_against: Average xG conceded per game
    - avg_possession: Average possession %
    
    These stats help predict how teams will perform.
    """
    team_stats = {}
    
    for _, team in teams_df.iterrows():
        team_id = team['id']
        team_name = team['name']
        
        # Home matches
        home_matches = matches_df[matches_df['home_team'] == team_id]
        # Away matches
        away_matches = matches_df[matches_df['away_team'] == team_id]
        
        # Calculate xG for and against
        xg_for_home = home_matches['home_expected_goals_xg'].mean() if len(home_matches) > 0 else 0
        xg_for_away = away_matches['away_expected_goals_xg'].mean() if len(away_matches) > 0 else 0
        xg_against_home = home_matches['away_expected_goals_xg'].mean() if len(home_matches) > 0 else 0
        xg_against_away = away_matches['home_expected_goals_xg'].mean() if len(away_matches) > 0 else 0
        
        total_matches = len(home_matches) + len(away_matches)
        
        if total_matches > 0:
            # Weighted average based on home/away split
            avg_xg_for = (xg_for_home * len(home_matches) + xg_for_away * len(away_matches)) / total_matches
            avg_xg_against = (xg_against_home * len(home_matches) + xg_against_away * len(away_matches)) / total_matches
        else:
            avg_xg_for = 1.3  # League average ~1.3 xG per game
            avg_xg_against = 1.3
        
        team_stats[team_id] = {
            'team_id': team_id,
            'team_name': team_name,
            'elo': team['elo'],
            'avg_xg_for': avg_xg_for,
            'avg_xg_against': avg_xg_against,
            'xg_for_home': xg_for_home,
            'xg_for_away': xg_for_away,
            'xg_against_home': xg_against_home,
            'xg_against_away': xg_against_away,
            'strength_attack_home': team['strength_attack_home'],
            'strength_attack_away': team['strength_attack_away'],
            'strength_defence_home': team['strength_defence_home'],
            'strength_defence_away': team['strength_defence_away'],
        }
    
    return pd.DataFrame(team_stats.values())


def calculate_rolling_form(player_gw_df, window=6):
    """
    Calculate rolling form features for each player.
    
    Uses the last N gameweeks to calculate:
    - Rolling average points
    - Rolling average minutes
    - Form trend (improving/declining)
    
    The window=6 emphasizes recent form as requested.
    
    Args:
        player_gw_df: Per-gameweek player stats
        window: Number of games to look back (default 6)
    
    Returns:
        pd.DataFrame: Player stats with rolling features
    """
    df = player_gw_df.copy()
    
    # Sort by player and gameweek
    df = df.sort_values(['id', 'season', 'gw'])
    
    # Rolling average points (last N games)
    # shift(1) prevents data leakage - only uses PAST games
    df[f'last_{window}_avg_points'] = df.groupby('id')['event_points'].transform(
        lambda x: x.rolling(window, min_periods=1).mean().shift(1)
    )
    
    # Rolling average minutes
    df[f'last_{window}_avg_minutes'] = df.groupby('id')['minutes'].transform(
        lambda x: x.rolling(window, min_periods=1).mean().shift(1)
    )
    
    # Shorter window for recent form (last 3)
    df['last_3_avg_points'] = df.groupby('id')['event_points'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().shift(1)
    )
    
    # Form trend: are they improving or declining?
    # Positive = improving, negative = declining
    df['form_trend'] = df[f'last_3_avg_points'] - df[f'last_{window}_avg_points']
    
    # Fill NaN with defaults for players with no history
    df[f'last_{window}_avg_points'] = df[f'last_{window}_avg_points'].fillna(2.0)
    df[f'last_{window}_avg_minutes'] = df[f'last_{window}_avg_minutes'].fillna(60.0)
    df['last_3_avg_points'] = df['last_3_avg_points'].fillna(2.0)
    df['form_trend'] = df['form_trend'].fillna(0.0)
    
    return df


def prepare_training_data(player_gw_df, teams_df, matches_df, players_df):
    """
    Prepare features (X) and target (y) for ML training.
    
    Features include:
    - Player form (last 6 games rolling average)
    - Player xG, xA rates (from playerstats)
    - Team Elo
    - Opponent Elo
    - Home/away
    - Position
    
    Target: event_points (points scored in that gameweek)
    """
    df = player_gw_df.copy()
    
    # Calculate team stats from matches
    team_stats = calculate_team_stats(matches_df, teams_df)
    
    # Map team info to players (need to get player's team)
    # The playerstats has team info embedded - we need to merge
    
    # Calculate rolling form
    df = calculate_rolling_form(df, window=6)
    
    # Encode position
    # Note: In FPL-Elo-Insights, position is already in players.csv
    # We may need to merge or it might be in playerstats
    
    # Get position from first/second name if available, or use a default
    # For now, we'll use form-based features primarily
    
    # Features for ML
    feature_columns = [
        'last_6_avg_points',      # Form (last 6 games)
        'last_3_avg_points',      # Recent form (last 3 games)
        'form_trend',             # Improving or declining
        'last_6_avg_minutes',     # Playing time consistency
        'form',                   # FPL's built-in form stat
        'now_cost',               # Price (proxy for quality)
        'selected_by_percent',    # Ownership
    ]
    
    # Only keep rows with valid features
    available_features = [col for col in feature_columns if col in df.columns]
    
    if not available_features:
        print("  Warning: No features found!")
        return None, None, df
    
    # Drop rows with NaN in features
    df_clean = df.dropna(subset=available_features)
    
    X = df_clean[available_features]
    y = df_clean['event_points']  # Target: points in that gameweek
    
    return X, y, df_clean


def process_data(seasons=None, save_processed=True):
    """
    Main data processing pipeline.
    
    Args:
        seasons: List of seasons to process (default: current season 2025-2026)
        save_processed: Whether to save processed data
    
    Returns:
        tuple: (X, y, df_processed)
    """
    if seasons is None:
        # Use current season which has the "By Gameweek" structure with per-GW stats
        # 2024-2025 has a different structure without per-gameweek breakdowns
        seasons = ['2025-2026']
    
    print("=" * 60)
    print("FPL Data Processing Pipeline (FPL-Elo-Insights)")
    print("=" * 60)
    
    all_data = []
    
    for season in seasons:
        print(f"\n--- Processing {season} ---")
        
        # Load data
        print("\n1. Loading teams with Elo ratings...")
        teams = load_teams_with_elo(season)
        
        print("\n2. Loading player gameweek stats...")
        player_gw = load_player_gameweek_stats(season)
        
        print("\n3. Loading matches with team xG...")
        matches = load_matches_with_team_xg(season)
        
        print("\n4. Loading player info...")
        players = load_players(season)
        
        if len(player_gw) > 0:
            all_data.append(player_gw)
    
    if not all_data:
        raise ValueError("No data loaded!")
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n--- Combined Data ---")
    print(f"  Total records: {len(combined)}")
    
    # Process features
    print("\n5. Calculating rolling form features...")
    df_processed = calculate_rolling_form(combined, window=6)
    
    print("\n6. Preparing training data...")
    X, y, df_clean = prepare_training_data(
        df_processed, 
        teams if 'teams' in dir() else pd.DataFrame(),
        matches if 'matches' in dir() else pd.DataFrame(),
        players if 'players' in dir() else pd.DataFrame()
    )
    
    if X is not None:
        print(f"\n  Features: {X.columns.tolist()}")
        print(f"  Training samples: {len(X)}")
        print(f"  Target mean: {y.mean():.2f}, std: {y.std():.2f}")
    
    if save_processed:
        output_path = Path(__file__).parent / "processed_data.csv"
        df_clean.to_csv(output_path, index=False)
        print(f"\n✓ Saved processed data to: {output_path}")
    
    print("\n" + "=" * 60)
    print("Data processing complete!")
    print("=" * 60)
    
    return X, y, df_clean


# Run if executed directly
if __name__ == '__main__':
    X, y, df = process_data()
    
    if X is not None:
        print(f"\nDataset Summary:")
        print(f"  Shape: {X.shape}")
        print(f"  Features: {list(X.columns)}")
        print(f"\nTarget (event_points) statistics:")
        print(f"  Mean: {y.mean():.2f}")
        print(f"  Std: {y.std():.2f}")
        print(f"  Min: {y.min()}, Max: {y.max()}")
