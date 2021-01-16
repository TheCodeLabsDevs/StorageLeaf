from typing import List

from pydantic import BaseModel


# ===== special =====

class Status(BaseModel):
    message: str


class Version(BaseModel):
    name: str
    code: int
    date: str

    class Config:
        schema_extra = {
            'example': {
                'name': 'v1.0.0',
                'code': 1,
                'date': '28.12.20',
            }
        }


class MinMax(BaseModel):
    min: float or None
    max: float or None


# ===== measurement =====
class Measurement(BaseModel):
    id: int
    value: str
    timestamp: str
    sensorId: int

    class Config:
        orm_mode = True


class MeasurementCreate(BaseModel):
    value: str
    sensorId: int


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


class Sensor(SensorBase):
    id: int
    name: str
    type: str
    deviceId: int

    class Config:
        orm_mode = True


# ===== device =====
class Device(BaseModel):
    id: int
    name: str
    sensors: List[SensorBase]

    class Config:
        orm_mode = True


class DeviceCreate(BaseModel):
    name: str


# ===== send multiple measurements =====

class SensorValue(BaseModel):
    name: str
    type: str
    value: str


class MultipleMeasurements(BaseModel):
    deviceName: str
    sensors: List[SensorValue]
