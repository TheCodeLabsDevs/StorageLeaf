import secrets

from fastapi import Security, HTTPException, Query
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from Settings import SETTINGS
from logic.database.Database import SessionLocal


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


API_KEY_HEADER = APIKeyHeader(name='apiKey')


async def check_api_key(apiKey: str = Security(API_KEY_HEADER)):
    expectedApiKey = SETTINGS['api']['key']
    if not secrets.compare_digest(expectedApiKey, apiKey):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='apiKey invalid')


START_DATE_TIME: str = Query(default='2021-01-16 18:15:22',
                             description='The start date and time of the date range that should be taken into account.')
END_DATE_TIME: str = Query(default='2021-01-16 19:15:22',
                           description='The end date and time of the date range that should be taken into account.')
