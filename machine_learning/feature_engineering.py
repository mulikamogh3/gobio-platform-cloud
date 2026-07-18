import pandas as pd
import numpy as np

def generate_features(df):
    """
    Applies feature engineering to the preprocessed GoBioAI telemetry.
    Generates thermal, energetic, and temporal features.
    """
    print(f"\n--- Starting Feature Engineering ---")
    df = df.copy()

    # 1. Thermal Features
    if 'temperature' in df.columns and 'target_temperature' in df.columns:
        df['temp_diff_from_target'] = df['temperature'] - df['target_temperature']
        df['temp_rate_of_change'] = df['temperature'].diff().fillna(0)

    # 2. Energetic Features
    if 'power' in df.columns:
        df['power_trend'] = df['power'].diff().fillna(0)
        # Assuming readings are every second; cumulative power over time
        df['energy_consumed_ws'] = df['power'].cumsum() 

    # 3. Runtime Features (Cumulative sum of active states)
    if 'heater_status' in df.columns:
        df['heater_runtime_sec'] = df['heater_status'].cumsum()
    
    # 4. Process Percentages (Simplified heuristics)
    if 'target_temperature' in df.columns and 'temperature' in df.columns:
        # Prevent division by zero
        safe_target = df['target_temperature'].replace(0, 1)
        df['heating_progress_pct'] = (df['temperature'] / safe_target) * 100
        df['heating_progress_pct'] = df['heating_progress_pct'].clip(0, 100)

    # Drop any new NaNs created by diff() functions
    df = df.fillna(0)

    print(f"Features generated: {list(df.columns)}")
    print(f"--- Feature Engineering Complete ---\n")
    
    return df
