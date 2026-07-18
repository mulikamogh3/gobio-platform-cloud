import pandas as pd
import numpy as np

def preprocess_telemetry(raw_data):
    """
    Automatically preprocesses raw ESP32 JSON telemetry for the ML pipeline.
    Handles both single JSON objects (live prediction) and lists of objects (batch training).
    """
    # 1. Detect single object vs list and convert to DataFrame
    if isinstance(raw_data, dict):
        df = pd.DataFrame([raw_data])
    elif isinstance(raw_data, list):
        df = pd.DataFrame(raw_data)
    else:
        raise ValueError("Input must be a JSON object (dict) or a list of objects.")

    print(f"\n--- Initial DataFrame Shape: {df.shape} ---")
    
    # 2. Remove duplicates
    initial_len = len(df)
    df = df.drop_duplicates()
    
    # 3. Handle missing values 
    df = df.ffill().bfill()
    
    # 4. Convert ON/OFF and TRUE/FALSE into 1/0
    bool_mapping = {True: 1, False: 0, "TRUE": 1, "FALSE": 0, "ON": 1, "OFF": 0, "on": 1, "off": 0}
    for col in df.columns:
        if df[col].apply(lambda x: x in bool_mapping.keys()).any():
            df[col] = df[col].map(bool_mapping).fillna(df[col])

    # 5. Convert AUTO/MANUAL into numerical values
    if 'mode' in df.columns:
        mode_mapping = {"AUTO": 1, "MANUAL": 0, "auto": 1, "manual": 0}
        df['mode'] = df['mode'].map(mode_mapping).fillna(df['mode'])

    # 6. Encode categorical columns (process, device_status)
    if 'process' in df.columns:
        df = pd.get_dummies(df, columns=['process'], dummy_na=False, dtype=int)
        
    if 'device_status' in df.columns:
        df = pd.get_dummies(df, columns=['device_status'], dummy_na=False, dtype=int)

    # 7. Convert timestamps into datetime and generate features
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month

    # 8. Remove unnecessary columns
    cols_to_drop = ['machine_id', 'serial_number', 'firmware_version', 'hardware_version', 'wifi_ssid', 'timestamp']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # 9. Detect invalid sensor values and filter them (only for batch training)
    # We don't filter during live inference (single row) so we don't return an empty DataFrame
    if len(df) > 1:
        if 'temperature' in df.columns:
            df = df[(df['temperature'] >= 0.0) & (df['temperature'] <= 150.0)]
        if 'voltage' in df.columns:
            df = df[(df['voltage'] >= 0.0) & (df['voltage'] <= 300.0)]

    print(f"--- Preprocessing Complete ---")
    print(f"Rows removed (duplicates/invalid): {initial_len - len(df)}")
    print(f"Final Shape: {df.shape}")
    print(f"Columns ready for engineering: {list(df.columns)}\n")

    return df