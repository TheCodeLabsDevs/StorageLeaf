from typing import List

from pydantic import BaseModel


class SensorBase(BaseModel):
    id: int
    name: str
    type: str


class SensorCreate(BaseModel):
    name: str
    type: str


class Sensor(BaseModel):
    id: int
    name: str
    type: str
    deviceId: int

    class Config:
        orm_mode = True


class DeviceBase(BaseModel):
    id: int
    name: str


class DeviceCreate(BaseModel):
    name: str


class Device(DeviceBase):
    sensors: List[SensorBase]

    class Config:
        orm_mode = True
