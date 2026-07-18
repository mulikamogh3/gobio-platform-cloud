from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    machine_id: str

class LiveData(DeviceBase):
    # We use Optional for static data we don't necessarily need to store every second
    type: str = "live_data"
    machine_name: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    
    timestamp: int  # ESP32 sends UNIX timestamp (e.g., 1751451000)
    uptime_sec: int
    
    mode: str
    process: str
    process_step: int
    process_running: bool
    process_paused: bool
    process_completed: bool
    emergency_stop: bool
    batch_number: int
    recipe_name: str
    
    temperature: float
    target_temperature: float
    holding_time_sec: int
    holding_elapsed_sec: int
    holding_remaining_sec: int
    cooling_target_temperature: float
    
    heater_enabled: bool
    heater_status: str
    heater_on_temperature: float
    heater_off_temperature: float
    
    cooler_enabled: bool
    cooler_status: str
    cooler_on_temperature: float
    cooler_off_temperature: float
    
    stirrer_enabled: bool
    stirrer_status: str
    
    voltage: float
    current: float
    power: float
    energy: float
    frequency: float
    power_factor: float
    
    heater_runtime_sec: int
    cooler_runtime_sec: int
    stirrer_runtime_sec: int
    
    wifi_connected: bool
    wifi_ssid: Optional[str] = None
    wifi_rssi: Optional[int] = None
    server_connected: Optional[bool] = None
    last_sync_sec: Optional[int] = None
    alarm: bool
    alarm_code: Optional[int] = None
    alarm_message: Optional[str] = None
    device_status: str

class ManualCommand(DeviceBase):
    mode: str = Field(default="MANUAL")
    command: str
    heater_state: bool
    cooler_state: bool
    stirrer_state: bool

class AutoCommand(DeviceBase):
    mode: str = Field(default="AUTO")
    command: str
    recipe_name: str
    target_temperature: float
    holding_time_sec: int
