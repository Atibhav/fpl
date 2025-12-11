"""
Baseline ML Models for FPL Points Prediction
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler


# Path to save trained models
MODELS_PATH = Path(__file__).parent.parent / "models"
MODELS_PATH.mkdir(exist_ok=True)


def load_processed_data():
    """
    Load the processed training data from CSV.
    
    Returns:
        tuple: (X, y) - features DataFrame and target Series
    """
    data_path = Path(__file__).parent.parent / "data" / "processed_data.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {data_path}. "
            "Run data_processor.py first!"
        )
    
    df = pd.read_csv(data_path)
    
    # Feature columns (same as in data_processor.py)
    feature_columns = [
        'last_6_avg_points',
        'last_3_avg_points', 
        'form_trend',
        'last_6_avg_minutes',
        'form',
        'now_cost',
        'selected_by_percent',
    ]
    
    # Only use columns that exist in the data
    available_features = [col for col in feature_columns if col in df.columns]
    
    X = df[available_features]
    y = df['event_points']  # Target: points in that gameweek
    
    return X, y, available_features


def train_linear_regression(X, y, model_name='linear_regression'):
    """
    Train a Linear Regression model.
    
    Args:
        X: Feature DataFrame
        y: Target Series
        model_name: Name for saving the model
    
    Returns:
        tuple: (model, metrics_dict)
    """
    print(f"\n{'='*50}")
    print("Training Linear Regression Model")
    print(f"{'='*50}")
    
    # Split data: 70% training, 30% testing
    # random_state ensures reproducibility (same split every time)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.3, 
        random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Make predictions on test set
    y_pred = model.predict(X_test)
    
    # Calculate evaluation metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Cross-validation for more robust evaluation
    # cv=5 means 5-fold cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    cv_rmse = np.sqrt(-cv_scores.mean())
    
    metrics = {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'cv_rmse': cv_rmse
    }
    
    print(f"\n--- Evaluation Metrics ---")
    print(f"RMSE: {rmse:.3f} (lower is better)")
    print(f"MAE: {mae:.3f} (lower is better)")
    print(f"R²: {r2:.3f} (higher is better, max 1.0)")
    print(f"CV RMSE: {cv_rmse:.3f} (5-fold cross-validation)")
    
    # Print feature importance (coefficients)
    print(f"\n--- Feature Importance (Coefficients) ---")
    for feature, coef in zip(X.columns, model.coef_):
        print(f"  {feature}: {coef:.4f}")
    print(f"  Intercept: {model.intercept_:.4f}")
    
    # Save the model
    model_path = MODELS_PATH / f"{model_name}.pkl"
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to: {model_path}")
    
    return model, metrics


def train_ridge_regression(X, y, alpha=1.0, model_name='ridge_regression'):
    """
    Train a Ridge Regression model.
    
    Ridge Regression is Linear Regression with L2 regularization.
    It adds a penalty term to prevent overfitting:
    
    Loss = MSE + α * Σ(β²)
    
    Where α (alpha) controls regularization strength:
    - Higher α = more regularization = simpler model
    - Lower α = less regularization = more like standard linear regression
    
    University Concept: Regularization prevents overfitting by penalizing
    large coefficients, making the model more generalizable.
    
    Args:
        X: Feature DataFrame
        y: Target Series
        alpha: Regularization strength (default 1.0)
        model_name: Name for saving the model
    
    Returns:
        tuple: (model, metrics_dict)
    """
    print(f"\n{'='*50}")
    print(f"Training Ridge Regression (α={alpha})")
    print(f"{'='*50}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Scale features for Ridge (important for regularization)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Ridge model
    model = Ridge(alpha=alpha)
    model.fit(X_train_scaled, y_train)
    
    # Predict and evaluate
    y_pred = model.predict(X_test_scaled)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics = {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'alpha': alpha
    }
    
    print(f"\n--- Evaluation Metrics ---")
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R²: {r2:.3f}")
    
    # Save model and scaler together
    model_path = MODELS_PATH / f"{model_name}.pkl"
    scaler_path = MODELS_PATH / f"{model_name}_scaler.pkl"
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n✓ Model saved to: {model_path}")
    
    return model, metrics, scaler


def compare_models():
    """
    Train and compare different baseline models.
    
    Returns:
        dict: Results for each model
    """
    print("\n" + "="*60)
    print("FPL Points Prediction - Baseline Model Training")
    print("="*60)
    
    # Load data
    print("\nLoading processed data...")
    X, y, features = load_processed_data()
    print(f"Dataset: {len(X)} samples, {len(features)} features")
    print(f"Features: {features}")
    print(f"Target stats: mean={y.mean():.2f}, std={y.std():.2f}")
    
    results = {}
    
    # Train Linear Regression
    lr_model, lr_metrics = train_linear_regression(X, y)
    results['linear_regression'] = lr_metrics
    
    # Train Ridge Regression with different alpha values
    for alpha in [0.1, 1.0, 10.0]:
        ridge_model, ridge_metrics, _ = train_ridge_regression(
            X, y, 
            alpha=alpha, 
            model_name=f'ridge_alpha_{alpha}'
        )
        results[f'ridge_alpha_{alpha}'] = ridge_metrics
    
    # Summary
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    print(f"\n{'Model':<25} {'RMSE':<10} {'MAE':<10} {'R²':<10}")
    print("-" * 55)
    for name, metrics in results.items():
        print(f"{name:<25} {metrics['rmse']:<10.3f} {metrics['mae']:<10.3f} {metrics['r2']:<10.3f}")
    
    # Find best model
    best_model = min(results.items(), key=lambda x: x[1]['rmse'])
    print(f"\n✓ Best model by RMSE: {best_model[0]} (RMSE={best_model[1]['rmse']:.3f})")
    
    return results


if __name__ == '__main__':
    results = compare_models()

