from typing import List

from pydantic import BaseModel, Field
from typing import Optional


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
    min: float = None
    max: float = None


# ===== measurement =====
class Measurement(BaseModel):
    id: int
    value: str
    timestamp: str
    sensor_id: int

    class Config:
        orm_mode = True


class MeasurementCreate(BaseModel):
    value: str = Field(..., min_length=1)
    timestamp: Optional[str]
    sensor_id: int


class MeasurementUpdate(BaseModel):
    value: str = Field(..., min_length=1)


# ===== sensor =====
class SensorBase(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        orm_mode = True


class SensorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    device_id: int


class SensorUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)


class Sensor(SensorBase):
    id: int
    name: str
    type: str
    device_id: int

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
    name: str = Field(..., min_length=1)


# ===== send multiple measurements =====

class SensorValue(BaseModel):
    name: str
    type: str
    value: str


class MultipleMeasurements(BaseModel):
    deviceName: str
    sensors: List[SensorValue]
