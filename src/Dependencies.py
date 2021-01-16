import secrets

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from logic.databaseNew.Database import SessionLocal


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


API_KEY_HEADER = APIKeyHeader(name='apiKey')


async def check_api_key(apiKey: str = Security(API_KEY_HEADER)):
    from main import API_KEY
    if not secrets.compare_digest(API_KEY, apiKey):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='apiKey invalid')
