import secrets

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from Settings import SETTINGS
from logic.databaseNew.Database import SessionLocal


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
