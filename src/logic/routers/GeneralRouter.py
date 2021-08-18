from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Settings import VERSION
from logic.Dependencies import get_database
from logic.database import Schemas, DatabaseInfoProvider

router = APIRouter(
    prefix='/general',
    tags=['general']
)


@router.get('/version',
            summary='Gets information about the server version',
            response_model=Schemas.Version)
async def version():
    return Schemas.Version(**VERSION)


@router.get('/databaseInfo',
            summary='Gets information about the database',
            response_model=Schemas.DatabaseInfo)
async def databaseInfo(db: Session = Depends(get_database)):
    return DatabaseInfoProvider.get_database_info(db)
