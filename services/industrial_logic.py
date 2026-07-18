import datetime

def check_industrial_safety_override(sensor_data: dict):
    """
    Validates industrial safety limits BEFORE the ML model executes.
    Returns a forced response dictionary if safe limits are exceeded.
    Returns None if all values are within safe operating limits.
    """
    try:
        temperature = float(sensor_data.get("temperature", 0.0))
        power = float(sensor_data.get("power", 0.0))
        voltage = float(sensor_data.get("voltage", 0.0))
    except (TypeError, ValueError):
        return None

    reason = None
    if temperature > 100:
        reason = "Temperature exceeded safe operating limit (> 100°C)."
    elif power > 2500:
        reason = "Power exceeded safe operating limit (> 2500W)."
    elif voltage > 260:
        reason = "Voltage exceeded safe operating limit (> 260V)."

    if reason:
        # Log the safety override event
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- Industrial Safety Override Triggered ---")
        print(f"Timestamp:   {timestamp}")
        print(f"Temperature: {temperature}°C")
        print(f"Voltage:     {voltage}V")
        print(f"Power:       {power}W")
        print(f"Reason:      {reason}")
        print(f"Source:      Industrial Safety Override\n")
        
        return {
            "status": "Critical",
            "anomaly_detected": True,
            "label": "ANOMALY DETECTED",
            "prediction": "Anomaly",
            "confidence": 100,
            "source": "Industrial Safety Override",
            "reason": reason,
            "override": True
        }
        
    return None

def calculate_heater_decision(temperature: float, target_temperature: float) -> dict:
    """
    Module 3: AI Heater Decision Engine
    Calculates the recommended power, action, and status based on temperature differences.
    """
    if temperature < target_temperature:
        difference = target_temperature - temperature
        if difference > 20:
            power = 100
            action = "Maximum Heating"
            status = "Critical Heating Required"
        elif difference > 10:  # 10-20
            power = 75
            action = "Moderate Heating"
            status = "Heating Required"
        elif difference > 5:   # 5-10
            power = 50
            action = "Steady Heating"
            status = "Approaching Target"
        elif difference > 2:   # 2-5
            power = 25
            action = "Fine Tuning"
            status = "Near Target"
        else:                  # <= 2
            power = 10
            action = "Maintain Temperature"
            status = "Stable"
    else:
        difference = temperature - target_temperature
        if difference > 2:     # temperature > target_temperature + 2
            power = 0
            action = "Cooling Recommended"
            status = "Overheating"
        else:                  # temperature >= target_temperature and <= +2
            power = 0
            action = "Turn Heater OFF"
            status = "Pasteurization Temperature Reached"

    return {
        "recommended_power": power,
        "action": action,
        "status": status,
        "difference": round(difference, 2)
    }
