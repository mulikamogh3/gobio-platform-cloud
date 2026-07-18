from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
import datetime

class SensorData(Base):
    __tablename__ = "sensor_data"

    # 1. Base Info
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    uptime_sec = Column(Integer)

    # 2. Process Info
    mode = Column(String)
    process = Column(String)
    process_step = Column(Integer)
    process_running = Column(Boolean)
    process_paused = Column(Boolean)
    process_completed = Column(Boolean)
    emergency_stop = Column(Boolean)
    batch_number = Column(Integer)
    recipe_name = Column(String)

    # 3. Thermal Data
    temperature = Column(Float)
    target_temperature = Column(Float)
    holding_time_sec = Column(Integer)
    holding_elapsed_sec = Column(Integer)
    holding_remaining_sec = Column(Integer)
    cooling_target_temperature = Column(Float)

    # 4. Hardware Relays
    heater_enabled = Column(Boolean)
    heater_status = Column(String) # ESP32 sends "ON"/"OFF" now instead of True/False
    cooler_enabled = Column(Boolean)
    cooler_status = Column(String)
    stirrer_enabled = Column(Boolean)
    stirrer_status = Column(String)

    # 5. Electrical Data
    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)
    energy = Column(Float)
    frequency = Column(Float)
    power_factor = Column(Float)

    # 6. Runtimes & System
    heater_runtime_sec = Column(Integer)
    cooler_runtime_sec = Column(Integer)
    stirrer_runtime_sec = Column(Integer)
    wifi_connected = Column(Boolean)
    alarm = Column(Boolean)
    device_status = Column(String)
