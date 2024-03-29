from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# ===== special =====

class Status(BaseModel):
    message: str


class Version(BaseModel):
    name: str
    code: int
    date: str

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'v1.0.0',
                'code': 1,
                'date': '28.12.20',
            }
        }


class DatabaseInfo(BaseModel):
    number_of_measurements: int
    size_on_disk_in_mb: int

    class Config:
        json_schema_extra = {
            'example': {
                'number_of_measurements': 1000,
                'size_on_disk_in_mb': 14
            }
        }


class DatabaseCleanupStatus(str, Enum):
    UNDEFINED = 'UNDEFINED'
    RUNNING = 'RUNNING'
    FINISHED = 'FINISHED'


class DatabaseCleanupInfo(BaseModel):
    status: DatabaseCleanupStatus
    before: DatabaseInfo = None
    after: DatabaseInfo = None
    difference: DatabaseInfo = None
    startTime: datetime
    endTime: datetime


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
        from_attributes = True


class MeasurementCreate(BaseModel):
    value: str = Field(..., min_length=1)
    timestamp: str | None = None
    sensor_id: int


class MeasurementUpdate(BaseModel):
    value: str = Field(..., min_length=1)


# ===== sensor =====
class SensorBase(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True


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
        from_attributes = True


# ===== device =====
class Device(BaseModel):
    id: int
    name: str
    sensors: List[SensorBase]

    class Config:
        from_attributes = True


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


# ===== scheduled jobs =====
class ScheduledJob(BaseModel):
    job_id: str
    run_frequency: str
    next_run: str

    class Config:
        json_schema_extra = {
            'example': {
                'job_id': 'my job id',
                'run_frequency': 'interval[0:05:00]',
                'next_run': '2021-09-30 22:12:09.397935+2:00'
            }
        }


class ScheduledJobStatus(BaseModel):
    jobs: List[ScheduledJob]
    job_results: List[DatabaseCleanupInfo]
