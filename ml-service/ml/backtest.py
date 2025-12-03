import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
import os

DATA_PATH = Path(__file__).parent.parent / "data" / "raw" / "FPL-Elo-Insights"


def load_season_data(season='2025-2026'):
    gw_path = DATA_PATH / "data" / season / "By Gameweek"
    
    if not gw_path.exists():
        print(f"Data not found at {gw_path}")
        return None
    
    all_data = []
    gw_folders = sorted([f for f in os.listdir(gw_path) if f.startswith('GW')])
    
    for gw_folder in gw_folders:
        stats_file = gw_path / gw_folder / "player_gameweek_stats.csv"
        if stats_file.exists():
            df = pd.read_csv(stats_file)
            df['gw'] = int(gw_folder.replace('GW', ''))
            all_data.append(df)
    
    if not all_data:
        return None
    
    combined = pd.concat(all_data, ignore_index=True)
    return combined.sort_values(['id', 'gw'])


def prepare_features(df):
    df = df.copy()
    df = df.sort_values(['id', 'gw'])
    
    df['last_3_avg_points'] = df.groupby('id')['event_points'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().shift(1)
    )
    df['last_6_avg_points'] = df.groupby('id')['event_points'].transform(
        lambda x: x.rolling(6, min_periods=1).mean().shift(1)
    )
    df['last_3_avg_minutes'] = df.groupby('id')['minutes'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().shift(1)
    )
    
    df['form_trend'] = df['last_3_avg_points'] - df['last_6_avg_points']
    
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    
    for col in ['last_3_avg_points', 'last_6_avg_points', 'last_3_avg_minutes', 'form_trend']:
        df[col] = df[col].clip(-50, 50)
    
    return df


def run_backtest(min_train_weeks=4):
    print("=" * 60)
    print("BACKTEST: Walk-Forward Validation")
    print("=" * 60)
    
    print("\n1. Loading data...")
    df = load_season_data()
    if df is None:
        print("Failed to load data")
        return None
    
    print(f"   Loaded {len(df)} records")
    print(f"   Gameweeks: {df['gw'].min()} to {df['gw'].max()}")
    
    print("\n2. Preparing features...")
    df = prepare_features(df)
    
    feature_cols = ['last_3_avg_points', 'last_6_avg_points', 'last_3_avg_minutes', 'form_trend']
    target_col = 'event_points'
    
    gameweeks = sorted(df['gw'].unique())
    
    if len(gameweeks) < min_train_weeks + 1:
        print(f"Not enough gameweeks. Need at least {min_train_weeks + 1}, have {len(gameweeks)}")
        return None
    
    print(f"\n3. Running walk-forward validation...")
    print(f"   Training starts with GW 1-{min_train_weeks}")
    print(f"   Testing on GW {min_train_weeks + 1} onwards\n")
    
    results = []
    all_predictions = []
    all_actuals = []
    
    for test_gw in gameweeks[min_train_weeks:]:
        train_data = df[df['gw'] < test_gw]
        test_data = df[df['gw'] == test_gw]
        
        if len(train_data) == 0 or len(test_data) == 0:
            continue
        
        X_train = train_data[feature_cols]
        y_train = train_data[target_col]
        X_test = test_data[feature_cols]
        y_test = test_data[target_col]
        
        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        
        results.append({
            'gameweek': test_gw,
            'train_size': len(train_data),
            'test_size': len(test_data),
            'rmse': rmse,
            'mae': mae
        })
        
        all_predictions.extend(predictions)
        all_actuals.extend(y_test.values)
        
        print(f"   GW{test_gw}: RMSE={rmse:.2f}, MAE={mae:.2f} (tested on {len(test_data)} players)")
    
    print("\n" + "=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)
    
    overall_rmse = np.sqrt(mean_squared_error(all_actuals, all_predictions))
    overall_mae = mean_absolute_error(all_actuals, all_predictions)
    overall_r2 = r2_score(all_actuals, all_predictions)
    
    print(f"\nAcross all tested gameweeks:")
    print(f"  RMSE: {overall_rmse:.2f}")
    print(f"  MAE:  {overall_mae:.2f}")
    print(f"  R²:   {overall_r2:.3f}")
    
    rmse_values = [r['rmse'] for r in results]
    rmse_std = np.std(rmse_values)
    print(f"  RMSE std dev: {rmse_std:.2f}")
    
    return results


if __name__ == '__main__':
    results = run_backtest(min_train_weeks=4)
