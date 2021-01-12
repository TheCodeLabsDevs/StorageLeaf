import json
from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from logic.databaseNew import Models, Schemas, Crud
from logic.databaseNew.Database import engine, SessionLocal

Models.Base.metadata.create_all(bind=engine)

app = FastAPI()

with open('../settings.json', 'r', encoding='UTF-8') as f:
    settings = json.load(f)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Device(BaseModel):
    id: int
    name: str


@app.get('/devices/', response_model=List[Schemas.Device])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Crud.get_devices(db, skip=skip, limit=limit)


@app.get('/devices/{deviceId}', response_model=Schemas.Device)
def read_device(deviceId: int, db: Session = Depends(get_db)):
    device = Crud.get_device(db, deviceId=deviceId)
    if device is None:
        raise HTTPException(status_code=404, detail='Device not found')
    return device


@app.post("/devices/", response_model=Schemas.Device)
def create_user(device: Schemas.DeviceCreate, db: Session = Depends(get_db)):
    createdDevice = Crud.get_device_by_name(db, device.name)
    if createdDevice:
        raise HTTPException(status_code=400, detail="Device with this name already exists")
    return Crud.create_device(db=db, device=device)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
