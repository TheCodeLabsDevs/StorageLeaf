from datetime import datetime
from typing import List, Set

from sqlalchemy import and_, text
from sqlalchemy.orm import Session

from logic.database import Models, Schemas

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ===== devices =====

def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[Models.Device]:
    return db.query(Models.Device).offset(skip).limit(limit).all()


def get_device(db: Session, deviceId: int) -> Models.Device:
    return db.query(Models.Device).filter(Models.Device.id == deviceId).first()


def get_device_by_name(db: Session, name: str) -> Models.Device:
    return db.query(Models.Device).filter(Models.Device.name == name).first()


def create_device(db: Session, device: Schemas.DeviceCreate) -> Models.Device:
    dbDevice = Models.Device(name=device.name)
    db.add(dbDevice)
    db.commit()
    db.refresh(dbDevice)
    return dbDevice


def update_device(db: Session, deviceId: int, device: Schemas.DeviceCreate) -> Models.Device:
    existingDevice = get_device(db, deviceId)
    existingDevice.name = device.name
    db.commit()
    db.refresh(existingDevice)
    return existingDevice


def delete_device(db: Session, device: Schemas.Device):
    db.delete(device)
    db.commit()


# ===== sensors =====

def get_sensors(db: Session, skip: int = 0, limit: int = 100) -> List[Models.Sensor]:
    return db.query(Models.Sensor).offset(skip).limit(limit).all()


def get_sensor(db: Session, sensorId: int) -> Models.Sensor:
    return db.query(Models.Sensor).filter(Models.Sensor.id == sensorId).first()


def get_sensor_by_name_and_device_id(db: Session, sensorName: str, deviceId: int) -> Models.Sensor:
    return db.query(Models.Sensor).filter(and_(Models.Sensor.name == sensorName,
                                               Models.Sensor.device_id == deviceId)).first()


def create_sensor(db: Session, sensor: Schemas.SensorCreate) -> Models.Sensor:
    dbSensor = Models.Sensor(**sensor.dict())
    db.add(dbSensor)
    db.commit()
    db.refresh(dbSensor)
    return dbSensor


def update_sensor(db: Session, sensorId: int, sensor: Schemas.SensorUpdate) -> Models.Sensor:
    existingSensor = get_sensor(db, sensorId)
    existingSensor.name = sensor.name
    existingSensor.type = sensor.type
    db.commit()
    db.refresh(existingSensor)
    return existingSensor


def delete_sensor(db: Session, sensor: Schemas.Sensor):
    db.delete(sensor)
    db.commit()


# ===== measurements =====

def get_measurements(db: Session, startDateTime: str, endDateTime: str) -> List[Models.Measurement]:
    if startDateTime and endDateTime:
        return db.query(Models.Measurement).filter(and_(startDateTime <= Models.Measurement.timestamp,
                                                        endDateTime >= Models.Measurement.timestamp)).all()

    return db.query(Models.Measurement).all()


def get_measurements_for_sensor(db: Session, startDateTime: str,
                                endDateTime: str, sensorId: int) -> List[Models.Measurement]:
    if startDateTime and endDateTime:
        return db.query(Models.Measurement) \
            .filter(Models.Measurement.sensor_id == sensorId) \
            .filter(and_(startDateTime <= Models.Measurement.timestamp,
                         endDateTime >= Models.Measurement.timestamp)) \
            .order_by(Models.Measurement.timestamp.desc()) \
            .all()

    return db.query(Models.Measurement) \
        .filter(Models.Measurement.sensor_id == sensorId) \
        .order_by(Models.Measurement.timestamp.desc()) \
        .all()


def get_latest_measurement_for_sensor(db: Session, sensorId: int) -> Models.Measurement:
    return db.query(Models.Measurement) \
        .filter(Models.Measurement.sensor_id == sensorId) \
        .order_by(Models.Measurement.timestamp.desc()) \
        .first()


def get_first_measurement_for_sensor(db: Session, sensorId: int) -> Models.Measurement:
    return db.query(Models.Measurement) \
        .filter(Models.Measurement.sensor_id == sensorId) \
        .order_by(Models.Measurement.timestamp.asc()) \
        .first()


def get_measurement(db: Session, measurementId: int) -> Models.Measurement:
    return db.query(Models.Measurement).filter(Models.Measurement.id == measurementId).first()


def create_measurement(db: Session, measurement: Schemas.MeasurementCreate) -> Models.Measurement:
    if measurement.timestamp is None:
        measurement.timestamp = __get_current_datetime()

    dbMeasurement = Models.Measurement(**measurement.dict())
    db.add(dbMeasurement)
    db.commit()
    db.refresh(dbMeasurement)
    return dbMeasurement


def update_measurement(db: Session, measurementId: int, measurement: Schemas.MeasurementUpdate) -> Models.Measurement:
    existingMeasurement = get_measurement(db, measurementId)
    existingMeasurement.value = measurement.value
    db.commit()
    db.refresh(existingMeasurement)
    return existingMeasurement


def delete_measurement(db: Session, measurement: Schemas.Measurement):
    db.delete(measurement)
    db.commit()


def delete_multiple_measurements(db: Session, measurementIds: Set[int]):
    db.query(Models.Measurement).filter(Models.Measurement.id.in_(measurementIds)).delete()
    db.commit()


def get_total_number_of_measurements(db: Session) -> List[int]:
    return db.query(Models.Measurement).count()


def perform_vacuum(db: Session):
    db.execute(text('VACUUM'))


def __get_current_datetime():
    return datetime.strftime(datetime.now(), DATE_FORMAT)
