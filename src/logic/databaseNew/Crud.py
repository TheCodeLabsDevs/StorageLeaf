from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from logic.databaseNew import Models, Schemas

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# ===== devices =====


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Models.Device).offset(skip).limit(limit).all()


def get_device(db: Session, deviceId: int):
    return db.query(Models.Device).filter(Models.Device.id == deviceId).first()


def get_device_by_name(db: Session, name: str):
    return db.query(Models.Device).filter(Models.Device.name == name).first()


def create_device(db: Session, device: Schemas.DeviceCreate):
    dbDevice = Models.Device(name=device.name)
    db.add(dbDevice)
    db.commit()
    db.refresh(dbDevice)
    return dbDevice


def delete_device(db: Session, device: Schemas.Device):
    db.delete(device)
    db.commit()


# ===== sensors =====

def get_sensors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Models.Sensor).offset(skip).limit(limit).all()


def get_sensor(db: Session, sensorId: int):
    return db.query(Models.Sensor).filter(Models.Sensor.id == sensorId).first()


def get_sensor_by_name_and_device_id(db: Session, sensorName: str, deviceId: int):
    return db.query(Models.Sensor).filter(
        Models.Sensor.name == sensorName and Models.Sensor.deviceId == deviceId).first()


def create_sensor(db: Session, sensor: Schemas.SensorCreate):
    dbSensor = Models.Sensor(**sensor.dict())
    db.add(dbSensor)
    db.commit()
    db.refresh(dbSensor)
    return dbSensor


def delete_sensor(db: Session, sensor: Schemas.Sensor):
    db.delete(sensor)
    db.commit()


# ===== measurements =====

def get_measurements(db: Session, startDateTime: str, endDateTime: str):
    if startDateTime and endDateTime:
        return db.query(Models.Measurement).filter(and_(startDateTime <= Models.Measurement.timestamp,
                                                        endDateTime >= Models.Measurement.timestamp)).all()

    return db.query(Models.Measurement).all()


def get_measurements_for_sensor(db: Session, startDateTime: str, endDateTime: str, sensorId: int):
    if startDateTime and endDateTime:
        return db.query(Models.Measurement).filter(and_(startDateTime <= Models.Measurement.timestamp,
                                                        endDateTime >= Models.Measurement.timestamp,
                                                        Models.Measurement.sensorId == sensorId)).all()

    return db.query(Models.Measurement).filter(Models.Measurement.sensorId == sensorId).all()


def get_latest_measurement_for_sensor(db: Session, sensorId: int):
    return db.query(Models.Measurement) \
        .filter(Models.Measurement.sensorId == sensorId) \
        .order_by(Models.Measurement.timestamp.desc()) \
        .first()


def get_measurement(db: Session, measurementId: int):
    return db.query(Models.Measurement).filter(Models.Measurement.id == measurementId).first()


def create_measurement(db: Session, measurement: Schemas.MeasurementCreate):
    dbMeasurement = Models.Measurement(**measurement.dict(), timestamp=__get_current_datetime())
    db.add(dbMeasurement)
    db.commit()
    db.refresh(dbMeasurement)
    return dbMeasurement


def delete_measurement(db: Session, measurement: Schemas.Measurement):
    db.delete(measurement)
    db.commit()


def __get_current_datetime():
    return datetime.strftime(datetime.now(), DATE_FORMAT)
