from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from logic.Dependencies import get_database, check_api_key, START_DATE_TIME, END_DATE_TIME
from logic.database import Schemas, Crud
from logic.database.Schemas import Status, MinMax

router = APIRouter(tags=['measurement'])


@router.get('/measurement', response_model=List[Schemas.Measurement],
            summary='Gets all measurements',
            description='Number of results can be limited by specifying a date range')
async def read_measurements(startDateTime: str = START_DATE_TIME,
                            endDateTime: str = END_DATE_TIME,
                            db: Session = Depends(get_database)):
    return Crud.get_measurements(db, startDateTime=startDateTime, endDateTime=endDateTime)


@router.get('/measurement/{measurementId}', response_model=Schemas.Measurement,
            summary='Gets a specific measurement',
            responses={404: {'description': 'Measurement not found'}})
async def read_measurement(measurementId: int, db: Session = Depends(get_database)):
    measurement = Crud.get_measurement(db, measurementId=measurementId)
    if measurement is None:
        raise HTTPException(status_code=404, detail='Measurement not found')
    return measurement


@router.post('/measurement/', response_model=Schemas.Measurement,
             summary='Adds a new measurement',
             responses={404: {'description': 'No sensor with id "{measurement.sensor_id}" existing'}},
             dependencies=[Depends(check_api_key)])
async def create_measurement(measurement: Schemas.MeasurementCreate, db: Session = Depends(get_database)):
    existingSensor = Crud.get_sensor(db, measurement.sensor_id)
    if not existingSensor:
        raise HTTPException(status_code=404, detail=f'No sensor with id "{measurement.sensor_id}" existing')

    return Crud.create_measurement(db=db, measurement=measurement)


@router.put('/measurement/{measurementId}', response_model=Schemas.Measurement,
            summary='Updates a specific measurement',
            responses={404: {'description': 'Measurement not found'}},
            dependencies=[Depends(check_api_key)])
async def update_measurement(measurementId: int, measurement: Schemas.MeasurementUpdate, db: Session = Depends(get_database)):
    existingMeasurement = Crud.get_measurement(db, measurementId)
    if existingMeasurement is None:
        raise HTTPException(status_code=404, detail='Measurement not found')

    return Crud.update_measurement(db, measurementId=measurementId, measurement=measurement)


@router.delete('/measurement/{measurementId}', response_model=Status,
               summary='Deletes a specific measurementId',
               responses={404: {'description': 'Measurement not found'}},
               dependencies=[Depends(check_api_key)])
async def delete_measurement(measurementId: int, db: Session = Depends(get_database)):
    measurement = Crud.get_measurement(db, measurementId=measurementId)
    if measurement is None:
        raise HTTPException(status_code=404, detail='Measurement not found')

    Crud.delete_measurement(db, measurement)
    return Status(message=f'Deleted measurement {measurement.id}')


@router.get('/measurements/minMax', response_model=Schemas.MinMax,
            summary='Gets the minimum and maximum values for the given sensor ids',
            description='Number of checked values can be limited by specifying a date range')
async def get_min_and_max_for_sensor_ids(sensorIds: List[int] = Query(None),
                                         startDateTime: str = START_DATE_TIME,
                                         endDateTime: str = END_DATE_TIME,
                                         db: Session = Depends(get_database)):
    values = []
    for sensorId in sensorIds:
        measurementsForSensor = Crud.get_measurements_for_sensor(db, startDateTime, endDateTime, sensorId)
        for measurement in measurementsForSensor:
            values.append(float(measurement.value))

    if values:
        return MinMax(min=min(values), max=max(values))

    return MinMax()


@router.post('/measurements/', response_model=Schemas.Status,
             summary='Adds multiple measurements',
             description='Non-existent device and sensors will be created automatically',
             dependencies=[Depends(check_api_key)])
async def create_multiple_measurements(measurementsToAdd: Schemas.MultipleMeasurements,
                                       db: Session = Depends(get_database)):
    existingDevice = Crud.get_device_by_name(db, measurementsToAdd.deviceName)
    if not existingDevice:
        existingDevice = Crud.create_device(db, Schemas.DeviceCreate(name=measurementsToAdd.deviceName))

    for sensor in measurementsToAdd.sensors:
        existingSensor = Crud.get_sensor_by_name_and_device_id(db, sensor.name, existingDevice.id)
        if not existingSensor:
            existingSensor = Crud.create_sensor(db, Schemas.SensorCreate(name=sensor.name,
                                                                         type=sensor.type,
                                                                         device_id=existingDevice.id))
        Crud.create_measurement(db, Schemas.MeasurementCreate(value=sensor.value, sensor_id=existingSensor.id))

    return Status(message=f'Success')
