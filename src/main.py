import json

import uvicorn
from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from fastapi import FastAPI
from starlette.responses import RedirectResponse, JSONResponse

from Settings import SETTINGS
from logic import Constants
from logic.databaseNew import Models
from logic.databaseNew.Database import engine
from routers import DeviceRouter

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)

# create database tables
Models.Base.metadata.create_all(bind=engine)

with open('version.json', 'r', encoding='UTF-8') as f:
    VERSION = json.load(f)['version']

app = FastAPI(title=Constants.APP_NAME,
              version=VERSION['name'],
              description='The StorageLeaf API')
app.include_router(DeviceRouter.router)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


@app.get('/version')
async def version():
    return JSONResponse(content=VERSION)


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


