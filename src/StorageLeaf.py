import json
import os

import uvicorn
from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from fastapi import FastAPI
from starlette.responses import RedirectResponse, FileResponse

from Settings import SETTINGS
from logic import Constants
from logic.DiscoveryService import DiscoveryService
from logic.database import Models, Schemas
from logic.database.Database import engine
from logic.routers import DeviceRouter
from logic.routers import SensorRouter, MeasurementRouter

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)

databaseSettings = SETTINGS['database']

with open('version.json', 'r', encoding='UTF-8') as f:
    VERSION = json.load(f)['version']

# create database tables
Models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=Constants.APP_NAME,
              version=VERSION['name'],
              description='The StorageLeaf API',
              servers=[{'url': SETTINGS['api']['url'], 'description': f'{Constants.APP_NAME} API'}])


@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(url='/docs')


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(app.root_path, 'static', 'favicon.ico'), media_type='image/vnd.microsoft.icon')


@app.get('/version',
         summary='Gets information about the server version',
         tags=['general'],
         response_model=Schemas.Version)
async def version():
    return Schemas.Version(**VERSION)


app.include_router(DeviceRouter.router)
app.include_router(SensorRouter.router)
app.include_router(MeasurementRouter.router)

discoverySettings = SETTINGS['discovery']
discoverySettings['apiPort'] = SETTINGS['server']['port']
discoveryService = DiscoveryService(**discoverySettings)
discoveryService.start()

if __name__ == '__main__':
    serverSettings = SETTINGS['server']
    protocol = 'https' if serverSettings['useSSL'] else 'http'

    LOGGER.info(('{name} {versionName}({versionCode}) - '
                 'Listening on {protocol}://{listen}:{port}...'.format(name=Constants.APP_NAME,
                                                                       versionName=VERSION['name'],
                                                                       versionCode=VERSION['code'],
                                                                       protocol=protocol,
                                                                       listen=serverSettings['listen'],
                                                                       port=serverSettings['port'])))

    if serverSettings['useSSL']:
        uvicorn.run(app, host=serverSettings['listen'], port=serverSettings['port'],
                    ssl_keyfile=serverSettings['keyfile'],
                    ssl_certfile=serverSettings['certfile'])
    else:
        uvicorn.run(app, host=serverSettings['listen'], port=serverSettings['port'])
