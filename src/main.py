import json

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse, JSONResponse

from logic import Constants
from logic.databaseNew import Models
from logic.databaseNew.Database import engine
from routers import DeviceRouter

# create database tables
Models.Base.metadata.create_all(bind=engine)

with open('version.json', 'r', encoding='UTF-8') as f:
    versionInfo = json.load(f)['version']

with open('../settings.json', 'r', encoding='UTF-8') as f:
    settings = json.load(f)

API_KEY = settings['api']['key']

app = FastAPI(title=Constants.APP_NAME,
              version=versionInfo['name'],
              description='The StorageLeaf API')
app.include_router(DeviceRouter.router)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


@app.get('/version')
async def version():
    return JSONResponse(content=versionInfo)

if __name__ == '__main__':
    uvicorn.run(app, host=settings['server']['listen'], port=settings['server']['port'])
