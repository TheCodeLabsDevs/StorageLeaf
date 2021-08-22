from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Settings import VERSION, SETTINGS
from logic.Dependencies import get_database
from logic.database import Schemas, DatabaseInfoProvider
from logic.database.DatabaseCleaner import DatabaseCleaner, RetentionPolicy

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


@router.get('/databaseCleanup',
            summary='Cleans up the database by enforcing the configured retention policies',
            response_model=Schemas.DatabaseCleanupInfo)
async def databaseCleanup(db: Session = Depends(get_database)):
    infoBefore = DatabaseInfoProvider.get_database_info(db)

    retentionPolicies = SETTINGS['database']['retentionPolicies']
    policies = []
    for item in retentionPolicies:
        policies.append(RetentionPolicy(resolutionInMinutes=item['resolutionInMinutes'], ageInDays=item['ageInDays']))

    DatabaseCleaner(policies).clean(db, datetime.now())

    infoAfter = DatabaseInfoProvider.get_database_info(db)

    deletedMeasurements = infoBefore.number_of_measurements - infoAfter.number_of_measurements
    sizeFreed = infoBefore.size_on_disk_in_mb - infoAfter.size_on_disk_in_mb
    infoDifference = Schemas.DatabaseInfo(number_of_measurements=deletedMeasurements, size_on_disk_in_mb=sizeFreed)

    return Schemas.DatabaseCleanupInfo(before=infoBefore,  after=infoAfter,  difference=infoDifference)

