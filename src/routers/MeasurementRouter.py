from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from Dependencies import get_database, check_api_key, START_DATE_TIME, END_DATE_TIME
from logic.databaseNew import Schemas, Crud
from logic.databaseNew.Schemas import Status, MinMax

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
             responses={404: {'description': 'No sensor with id "{measurement.sensorId}" existing'}},
             dependencies=[Depends(check_api_key)])
async def create_measurement(measurement: Schemas.MeasurementCreate, db: Session = Depends(get_database)):
    existingSensor = Crud.get_sensor(db, measurement.sensorId)
    if not existingSensor:
        raise HTTPException(status_code=404, detail=f'No sensor with id "{measurement.sensorId}" existing')

    return Crud.create_measurement(db=db, measurement=measurement)


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

    return MinMax(min=None, max=None)
