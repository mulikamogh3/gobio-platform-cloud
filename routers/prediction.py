from fastapi import APIRouter, Body
from machine_learning.predict import make_prediction
from services.industrial_logic import check_industrial_safety_override

# Creates a dedicated router for all /prediction endpoints
router = APIRouter(
    prefix="/prediction",
    tags=["Machine Learning Inference"]
)

@router.post("/heating")
def predict_heating_time(sensor_data: dict = Body(...)):
    """Predicts the remaining heating time based on live ESP32 telemetry."""
    # Assumes you have trained and saved a model named 'heating_model.pkl'
    result = make_prediction(sensor_data, "heating_model.pkl")
    return result

@router.post("/health")
def predict_machine_health(sensor_data: dict = Body(...)):
    """Classifies the current health status of the pasteurizer."""
    # Assumes you have trained and saved a model named 'health_model.pkl'
    result = make_prediction(sensor_data, "health_model.pkl")
    return result

@router.post("/anomaly")
def detect_faults(sensor_data: dict = Body(...)):
    """Uses Isolation Forest to detect if the current reading is an anomaly."""
    
    # 1. Industrial Safety Override (Validates physics BEFORE ML)
    safety_override = check_industrial_safety_override(sensor_data)
    if safety_override:
        return safety_override
        
    # 2. Existing Machine Learning Model Execution
    result = make_prediction(sensor_data, "fault_model.pkl")
    # Isolation Forest returns -1 for anomalies and 1 for normal
    is_anomaly = True if result["prediction"] == -1 else False
    return {"status": "success", "anomaly_detected": is_anomaly}
