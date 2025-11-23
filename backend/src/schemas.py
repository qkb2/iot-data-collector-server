from typing import List

from pydantic import BaseModel


# --- Registration ---
class DeviceRegister(BaseModel):
    id: str
    sensors: List[str]


class DeviceOut(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


# --- Sending Data ---
class SingleSensorValue(BaseModel):
    name: str
    value: float


class SensorDataIn(BaseModel):
    id: str
    sensor_values: List[SingleSensorValue]
