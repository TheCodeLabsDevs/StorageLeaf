from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from Dependencies import get_database, check_api_key
from logic.databaseNew import Schemas, Crud
from logic.databaseNew.Schemas import Status

router = APIRouter(
    prefix='/sensor',
    tags=['sensor']
)


@router.get('/', response_model=List[Schemas.Sensor],
            summary='Gets all sensors')
async def read_sensors(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    return Crud.get_sensors(db, skip=skip, limit=limit)


@router.get('/{sensorId}', response_model=Schemas.Sensor,
            summary='Gets a specific sensor',
            responses={404: {'description': 'Sensor not found'}})
async def read_sensor(sensorId: int, db: Session = Depends(get_database)):
    sensor = Crud.get_sensor(db, sensorId=sensorId)
    if sensor is None:
        raise HTTPException(status_code=404, detail='Sensor not found')
    return sensor


@router.post('/', response_model=Schemas.Sensor,
             summary='Adds a new sensor',
             responses={400: {'description': 'A sensor called "{sensor.name}" already exists '
                                             '(ID: {existingSensor.id}) for device {sensor.deviceId}'},
                        404: {'description': 'No device with id "{sensor.deviceId}" existing'}},
             dependencies=[Depends(check_api_key)])
async def create_sensor(sensor: Schemas.SensorCreate, db: Session = Depends(get_database)):
    existingDevice = Crud.get_device(db, sensor.deviceId)
    if not existingDevice:
        raise HTTPException(status_code=404, detail=f'No device with id "{sensor.deviceId}" existing')

    existingSensor = Crud.get_sensor_by_name_and_device_id(db, sensor.name, sensor.deviceId)
    if existingSensor:
        raise HTTPException(status_code=400,
                            detail=f'A sensor called "{sensor.name}" already exists '
                                   f'(ID: {existingSensor.id}) for device {sensor.deviceId}')

    return Crud.create_sensor(db=db, sensor=sensor)


@router.delete('/{sensorId}', response_model=Status,
               summary='Deletes a specific sensor',
               description='All corresponding measurements will be deleted too.',
               responses={404: {'description': 'Sensor not found'}},
               dependencies=[Depends(check_api_key)])
async def delete_sensor(sensorId: int, db: Session = Depends(get_database)):
    sensor = Crud.get_sensor(db, sensorId=sensorId)
    if sensor is None:
        raise HTTPException(status_code=404, detail='Sensor not found')

    Crud.delete_sensor(db, sensor)
    return Status(message=f'Deleted sensor {sensor.id}')
