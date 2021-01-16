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

with open('../settings.json', 'r', encoding='UTF-8') as f:
    settings = json.load(f)

API_KEY = settings['api']['key']

app = FastAPI(title=Constants.APP_NAME,
              version=version['name'],
              description='The StorageLeaf API')
app.include_router(DeviceRouter.router)

if __name__ == '__main__':
    uvicorn.run(app, host=settings['server']['listen'], port=settings['server']['port'])
