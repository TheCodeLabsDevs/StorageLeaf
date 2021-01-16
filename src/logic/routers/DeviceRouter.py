from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from logic.Dependencies import get_database, check_api_key
from logic.database import Schemas, Crud
from logic.database.Schemas import Status

router = APIRouter(
    prefix='/device',
    tags=['device']
)


@router.get('/', response_model=List[Schemas.Device],
            summary='Gets all devices')
async def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    return Crud.get_devices(db, skip=skip, limit=limit)


@router.get('/{deviceId}', response_model=Schemas.Device,
            summary='Gets a specific device',
            responses={404: {'description': 'Device not found'}})
async def read_device(deviceId: int, db: Session = Depends(get_database)):
    device = Crud.get_device(db, deviceId=deviceId)
    if device is None:
        raise HTTPException(status_code=404, detail='Device not found')
    return device


@router.post('/', response_model=Schemas.Device,
             summary='Adds a new device',
             responses={400: {'description': 'Device with this name already exists'}},
             dependencies=[Depends(check_api_key)])
async def create_device(device: Schemas.DeviceCreate, db: Session = Depends(get_database)):
    createdDevice = Crud.get_device_by_name(db, device.name)
    if createdDevice:
        raise HTTPException(status_code=400, detail='Device with this name already exists')
    return Crud.create_device(db=db, device=device)


@router.put('/{deviceId}', response_model=Schemas.Device,
            summary='Updates a  device',
            responses={404: {'description': 'Device not found'}},
            dependencies=[Depends(check_api_key)])
async def update_device(deviceId: int, device: Schemas.DeviceCreate, db: Session = Depends(get_database)):
    createdDevice = Crud.get_device_by_name(db, device.name)
    if createdDevice:
        raise HTTPException(status_code=404, detail='Device not found')
    return Crud.update_device(db=db, deviceId=deviceId, device=device)


@router.delete('/{deviceId}', response_model=Status,
               summary='Deletes a specific device',
               description='All corresponding sensors and measurements will be deleted too.',
               responses={404: {'description': 'Device not found'}},
               dependencies=[Depends(check_api_key)])
async def delete_device(deviceId: int, db: Session = Depends(get_database)):
    device = Crud.get_device(db, deviceId=deviceId)
    if device is None:
        raise HTTPException(status_code=404, detail='Device not found')

    Crud.delete_device(db, device)
    return Status(message=f"Deleted device {device.id}")
