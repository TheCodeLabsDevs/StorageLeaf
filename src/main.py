import json

import uvicorn
from fastapi import FastAPI

from logic import Constants
from logic.databaseNew import Models
from logic.databaseNew.Database import engine
from routers import DeviceRouter

# create database tables
Models.Base.metadata.create_all(bind=engine)

with open('version.json', 'r', encoding='UTF-8') as f:
    version = json.load(f)['version']

app = FastAPI(title=Constants.APP_NAME,
              version=version['name'],
              description='The StorageLeaf API')
app.include_router(DeviceRouter.router)

with open('../settings.json', 'r', encoding='UTF-8') as f:
    settings = json.load(f)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
