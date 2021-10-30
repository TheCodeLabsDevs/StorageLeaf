import os

import uvicorn
from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.responses import RedirectResponse, FileResponse

from Settings import SETTINGS, VERSION
from logic import Constants
from logic.DatabaseCleanupService import DatabaseCleanupService
from logic.Dependencies import get_database
from logic.DiscoveryService import DiscoveryService
from logic.database import Models
from logic.database.Database import engine
from logic.routers import DeviceRouter, GeneralRouter, DatabaseRouter
from logic.routers import SensorRouter, MeasurementRouter

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)

DATABASE_SETTINGS = SETTINGS['database']

# create database tables
Models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=Constants.APP_NAME,
              version=VERSION['name'],
              servers=[{'url': SETTINGS['api']['url'], 'description': f'{Constants.APP_NAME} API'}],
              docs_url=None,
              redoc_url=None)

if 'cors_origins' in SETTINGS['server']:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SETTINGS['server']['cors_origins'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(url='/docs')


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(app.root_path, 'static', 'favicon.ico'), media_type='image/vnd.microsoft.icon')


@app.get('/docs', include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url='/openapi.json', title='The StorageLeaf API',
                               swagger_favicon_url=app.url_path_for('favicon'))


@app.get('/redoc', include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(openapi_url='/openapi.json', title='The StorageLeaf API',
                          redoc_favicon_url=app.url_path_for('favicon'))


@app.on_event("startup")
async def startup_event():
    cleanupSettings = SETTINGS['database']['cleanup']
    if cleanupSettings['automatic']['enable']:
        cleanupService = DatabaseCleanupService(cleanupSettings)

        try:
            cronTrigger = CronTrigger.from_crontab(cleanupSettings['automatic']['cronSchedule'])
        except ValueError as e:
            raise ValueError(f'Invalid syntax for settings option "cronSchedule": {str(e)}') from e

        from logic import JobScheduler
        JobScheduler.SCHEDULER.schedule_automatic_job(cleanupService.cleanup, [next(get_database())], cronTrigger)


app.include_router(GeneralRouter.router)
app.include_router(DatabaseRouter.router)
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
