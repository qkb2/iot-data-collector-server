from typing import List

from pydantic import BaseModel


Q31_DIV_VAL = 1 << 31


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
class SensorValueIn(BaseModel):
    sensor: str
    type: str
    value: int
    shift: int

    def normalized(self) -> float:
        return (self.value << self.shift) / Q31_DIV_VAL


class SensorDataIn(BaseModel):
    id: str
    sensor_values: List[SensorValueIn]
