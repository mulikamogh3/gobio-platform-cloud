import os
import joblib
import pandas as pd
from fastapi import HTTPException
from machine_learning.preprocessing import preprocess_telemetry
from machine_learning.feature_engineering import generate_features

MODEL_DIR = "machine_learning/models/"

def load_model(model_name: str):
    """Loads a trained Joblib model from disk safely."""
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{model_name}' not found. Please train the model first."
        )
    return joblib.load(filepath)

def make_prediction(live_json_data: dict, model_name: str):
    """
    1. Accepts raw JSON from the ESP32.
    2. Runs it through the preprocessing pipeline.
    3. Runs it through feature engineering.
    4. Feeds it to the loaded model and returns the result.
    """
    try:
        # Remove UI injected payload from the ML pipeline to prevent Pandas crash
        if isinstance(live_json_data, dict) and "heater_decision" in live_json_data:
            # We use copy() so we don't mutate the original request dictionary
            clean_data = live_json_data.copy()
            del clean_data["heater_decision"]
        else:
            clean_data = live_json_data
            
        # Step 1 & 2: Clean and Engineer
        df_clean = preprocess_telemetry(clean_data)
        df_features = generate_features(df_clean)
        
        # Step 3: Load Model
        model = load_model(model_name)
        
        # Step 4: Predict (Aligning columns to match training data)
        if hasattr(model, 'feature_names_in_'):
            # Convert existing columns to numeric, coercing any errors to 0
            for col in df_features.columns:
                df_features[col] = pd.to_numeric(df_features[col], errors='coerce').fillna(0)
            
            # Fill missing model features with 0
            for col in model.feature_names_in_:
                if col not in df_features.columns:
                    df_features[col] = 0.0
            
            # Keep only the trained features in the exact training order
            df_features = df_features[list(model.feature_names_in_)]
            
        prediction = model.predict(df_features)
        
        return {"status": "success", "prediction": float(prediction[0])}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
