from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from Dependencies import get_database, check_api_key
from logic.databaseNew import Schemas, Crud
from logic.databaseNew.Schemas import Status

router = APIRouter(
    prefix='/measurement',
    tags=['measurement']
)


@router.get('/', response_model=List[Schemas.Measurement],
            summary='Gets all measurements (Number of results can be limited by specifying a date range).')
async def read_measurements(startDateTime: str = Query('2020-01-20 18:15:22',
                                                       description='The start date and time of the date range '
                                                                   'that should be taken into account.'),
                            endDateTime: str = Query('2020-01-20 19:15:22',
                                                     description='The end date and time of the date range '
                                                                 'that should be taken into account.'),
                            db: Session = Depends(get_database)):
    return Crud.get_measurements(db, startDateTime=startDateTime, endDateTime=endDateTime)


@router.get('/{measurementId}', response_model=Schemas.Measurement,
            summary='Gets a specific measurement',
            responses={404: {'description': 'Measurement not found'}})
async def read_measurement(measurementId: int, db: Session = Depends(get_database)):
    measurement = Crud.get_measurement(db, measurementId=measurementId)
    if measurement is None:
        raise HTTPException(status_code=404, detail='Measurement not found')
    return measurement


@router.post('/', response_model=Schemas.Measurement,
             summary='Adds a new measurement',
             responses={404: {'description': 'No sensor with id "{measurement.sensorId}" existing'}},
             dependencies=[Depends(check_api_key)])
async def create_measurement(measurement: Schemas.MeasurementCreate, db: Session = Depends(get_database)):
    existingSensor = Crud.get_sensor(db, measurement.sensorId)
    if not existingSensor:
        raise HTTPException(status_code=404, detail=f'No sensor with id "{measurement.sensorId}" existing')

    return Crud.create_measurement(db=db, measurement=measurement)


@router.delete('/{measurementId}', response_model=Status,
               summary='Deletes a specific measurementId',
               responses={404: {'description': 'Measurement not found'}},
               dependencies=[Depends(check_api_key)])
async def delete_measurement(measurementId: int, db: Session = Depends(get_database)):
    measurement = Crud.get_measurement(db, measurementId=measurementId)
    if measurement is None:
        raise HTTPException(status_code=404, detail='Measurement not found')

    Crud.delete_measurement(db, measurement)
    return Status(message=f'Deleted measurement {measurement.id}')
