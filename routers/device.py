from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import schemas
import models
from database import get_db
from services.industrial_logic import calculate_heater_decision

router = APIRouter(
    prefix="/device",
    tags=["IoT Device Endpoints"]
)

# 1. The Ingestion API (For the ESP32)
@router.post("/data")
def receive_sensor_data(payload: schemas.LiveData, db: Session = Depends(get_db)):
    
    # 1. Convert the massive Pydantic payload into a dictionary
    # We exclude fields that exist in the JSON but not in our models.py database table
    data_dict = payload.model_dump(exclude={
        'type', 'machine_name', 'serial_number', 'firmware_version', 
        'hardware_version', 'wifi_ssid', 'wifi_rssi', 'server_connected', 
        'last_sync_sec', 'alarm_code', 'alarm_message',
        'heater_on_temperature', 'heater_off_temperature',
        'cooler_on_temperature', 'cooler_off_temperature'
    })
    
    # 2. The timestamp is now auto-parsed into a DateTime object by Pydantic
    # We just need to handle the case where it might be missing (None)
    data_dict['timestamp'] = payload.timestamp if payload.timestamp else datetime.utcnow()

    # 3. The Magic Trick: **data_dict automatically maps all 30 remaining fields into the database!
    new_data = models.SensorData(**data_dict)
    
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    print(f"✅ Full Industrial Data saved for {payload.machine_id}: Temp={payload.temperature}°C")
    return {"status": "success", "message": "Data safely stored in GoBioAI database"}

# 2. The LIVE API (Fetching from PostgreSQL)
@router.get("/live")
def get_live_data(db: Session = Depends(get_db)):
    # 1. Fetch the absolute latest row from the vault
    latest_data = db.query(models.SensorData).order_by(models.SensorData.id.desc()).first()
    
    if not latest_data:
        return {}
        
    # 2. Dynamically grab ALL 37 columns from the database row
    live_dict = {column.name: getattr(latest_data, column.name) for column in latest_data.__table__.columns}
    
    # 3. Safely override the heater_status so the React UI doesn't crash, 
    # while preserving the other 36 columns for the AI models!
    live_dict["heater_status"] = (latest_data.heater_status == "ON" or latest_data.heater_status is True)
    
    # 4. Inject Module 3: AI Heater Decision Engine
    temperature = live_dict.get("temperature", 0.0)
    target_temperature = live_dict.get("target_temperature", 0.0)
    live_dict["heater_decision"] = calculate_heater_decision(temperature, target_temperature)
    
    return live_dict

# 3. The HISTORY API (For the Analytics Charts)
@router.get("/history")
def get_historical_data(limit: int = 50, db: Session = Depends(get_db)):
    # Fetch the latest X records, ordered by newest first
    records = db.query(models.SensorData).order_by(models.SensorData.id.desc()).limit(limit).all()
    
    if not records:
        return []
        
    # Reverse the list so it reads chronologically (oldest -> newest) for the chart
    records.reverse()
    
    # Format the data cleanly for Recharts
    history_data = []
    for r in records:
        history_data.append({
            # Format time as HH:MM:SS for the X-axis
            "time": r.timestamp.strftime("%H:%M:%S") if r.timestamp else "00:00:00",
            "temperature": round(r.temperature or 0.0, 2),
            "target": round(r.target_temperature or 0.0, 2),
            "power": round(r.power or 0.0, 2)
        })
        
    return history_data
