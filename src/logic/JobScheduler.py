import logging
from datetime import datetime, timedelta
from typing import Callable, List

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tzlocal import get_localzone

from logic import Constants
from logic.database import Schemas
from logic.database.Schemas import DatabaseCleanupInfo

LOGGER = logging.getLogger(Constants.APP_NAME)
TIMEZONE = get_localzone()


class JobScheduler:
    ID_AUTO = 'Automatic cleanup'
    ID_MANUAL = 'Manual cleanup'

    STATE_IDLE = 0
    STATE_RUNNING = 1

    def __init__(self, ):
        self._scheduler = AsyncIOScheduler(logger=LOGGER)
        self._jobAutomatic = self._scheduler.add_job(func=dummyFunc, args=[], trigger='interval',
                                                     minutes=60, id=self.ID_AUTO, timezone=TIMEZONE)

        self._jobStatus = {
            self.ID_AUTO: self.STATE_IDLE,
            self.ID_MANUAL: self.STATE_IDLE
        }

        self._jobResults = []

        self._scheduler.start(paused=True)

        self._jobAutomatic.pause()

        self._scheduler.add_listener(self.job_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self._scheduler.resume()

    def job_event_listener(self, event: JobExecutionEvent):
        self._jobStatus[event.job_id] = self.STATE_IDLE

        if isinstance(event.retval, DatabaseCleanupInfo):
            self._jobResults.append(event.retval)

        if event.exception:
            LOGGER.error(f'Error executing job "{event.job_id}"')
        else:
            LOGGER.debug(f'Successfully finished job "{event.job_id}" (retval: {event.retval})')

    def schedule_automatic_job(self, func: Callable, args: List, cronTrigger: CronTrigger):
        self._jobAutomatic = self._jobAutomatic.modify(func=func, args=args)
        self._jobAutomatic = self._jobAutomatic.reschedule(trigger=cronTrigger, timezone=TIMEZONE)
        self._jobStatus[self.ID_AUTO] = self.STATE_RUNNING

    def run_manual_job(self, func: Callable, args: List):
        if self._jobStatus[self.ID_MANUAL] == self.STATE_RUNNING:
            raise JobAlreadyRunningError(f'Job "{self.ID_MANUAL}" is already running!')

        self._scheduler.add_job(func=func, args=args, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=5),
                                id=self.ID_MANUAL, timezone=TIMEZONE)
        self._jobStatus[self.ID_MANUAL] = self.STATE_RUNNING

    def get_scheduled_jobs(self) -> Schemas.ScheduledJobStatus:
        jobs = []
        for job in self._scheduler.get_jobs():
            scheduledJob = Schemas.ScheduledJob(job_id=str(job.id),
                                                run_frequency=str(job.trigger),
                                                next_run=str(job.next_run_time))
            jobs.append(scheduledJob)

        return Schemas.ScheduledJobStatus(jobs=jobs, job_results=self._jobResults)


def dummyFunc():
    pass


class JobAlreadyRunningError(Exception):
    pass


SCHEDULER: JobScheduler = JobScheduler()
