from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from Dependencies import get_database
from logic.databaseNew import Schemas, Crud

router = APIRouter(
    prefix='/device',
    tags=['device'],
    responses={404: {'description': 'Not found'}},
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
             responses={400: {'description': 'Device with this name already exists'}})
async def create_user(device: Schemas.DeviceCreate, db: Session = Depends(get_database)):
    createdDevice = Crud.get_device_by_name(db, device.name)
    if createdDevice:
        raise HTTPException(status_code=400, detail='Device with this name already exists')
    return Crud.create_device(db=db, device=device)
