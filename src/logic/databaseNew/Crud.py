from sqlalchemy.orm import Session

from logic.databaseNew import Models, Schemas


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
