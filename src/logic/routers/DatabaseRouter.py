from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Settings import SETTINGS
from logic.DatabaseCleanupService import DatabaseCleanupService
from logic.Dependencies import get_database, check_api_key
from logic.database import Schemas, DatabaseInfoProvider

router = APIRouter(
    prefix='/database',
    tags=['database']
)


@router.get('/databaseInfo',
            summary='Gets information about the database',
            response_model=Schemas.DatabaseInfo)
async def databaseInfo(db: Session = Depends(get_database)):
    return DatabaseInfoProvider.get_database_info(db)


@router.post('/databaseCleanup',
             summary='Initiates a database cleanup by enforcing the configured retention policies for each sensor',
             response_model=Schemas.Status,
             dependencies=[Depends(check_api_key)])
async def databaseCleanup(db: Session = Depends(get_database)):
    from logic import JobScheduler
    cleanupService = DatabaseCleanupService(SETTINGS['database']['cleanup'])
    try:
        JobScheduler.SCHEDULER.run_manual_job(cleanupService.cleanup, args=[db])
    except JobScheduler.JobAlreadyRunningError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Schemas.Status(message='Successfully triggered database cleanup')


@router.get('/databaseCleanup',
            summary='Provides the status of the all scheduled database cleanup jobs',
            response_model=Schemas.ScheduledJobStatus)
async def getStatus():
    from logic import JobScheduler
    return JobScheduler.SCHEDULER.get_scheduled_jobs()
