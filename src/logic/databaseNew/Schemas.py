from typing import List

from pydantic import BaseModel


class Status(BaseModel):
    message: str


# ===== sensor =====
class SensorBase(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        orm_mode = True


class SensorCreate(BaseModel):
    name: str
    type: str
    deviceId: int


class Sensor(BaseModel):
    id: int
    name: str
    type: str
    deviceId: int

    class Config:
        orm_mode = True


# ===== device =====
class DeviceBase(BaseModel):
    id: int
    name: str


class DeviceCreate(BaseModel):
    name: str


class Device(DeviceBase):
    sensors: List[SensorBase]

    class Config:
        orm_mode = True
