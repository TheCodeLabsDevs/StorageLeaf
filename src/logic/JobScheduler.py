import logging
from datetime import datetime, timedelta
from typing import Callable, List

import pytz
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from logic import Constants
from logic.database import Schemas

LOGGER = logging.getLogger(Constants.APP_NAME)
TIMEZONE = pytz.timezone('Europe/Berlin')


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

        self._scheduler.start(paused=True)

        self._jobAutomatic.pause()

        self._scheduler.add_listener(self.job_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self._scheduler.resume()

    def job_event_listener(self, event: JobExecutionEvent):
        self._jobStatus[event.job_id] = self.STATE_IDLE

        if event.exception:
            LOGGER.error(f'Error executing job "{event.job_id}"')
        else:
            LOGGER.debug(f'Successfully finished job "{event.job_id}" (retval: {event.retval})')

    def schedule_automatic_job(self, func: Callable, args: List, interval_in_minutes: int):
        self._jobAutomatic = self._jobAutomatic.modify(func=func, args=args)
        self._jobAutomatic = self._jobAutomatic.reschedule(trigger='interval', minutes=interval_in_minutes,
                                                           timezone=TIMEZONE)
        self._jobStatus[self.ID_AUTO] = self.STATE_RUNNING

    def run_manual_job(self, func: Callable, args: List):
        if self._jobStatus[self.ID_MANUAL] == self.STATE_RUNNING:
            raise JobAlreadyRunningError(f'Job "{self.ID_MANUAL}" is already running!')

        self._scheduler.add_job(func=func, args=args, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=5),
                                id=self.ID_MANUAL, timezone=TIMEZONE)
        self._jobStatus[self.ID_MANUAL] = self.STATE_RUNNING

    def get_scheduled_jobs(self) -> Schemas.ScheduledJobs:
        jobs = []
        for job in self._scheduler.get_jobs():
            scheduledJob = Schemas.ScheduledJob(job_id=str(job.id),
                                                run_frequency=str(job.trigger),
                                                next_run=str(job.next_run_time))
            jobs.append(scheduledJob)

        return Schemas.ScheduledJobs(jobs=jobs)


def dummyFunc():
    pass


class JobAlreadyRunningError(Exception):
    pass


SCHEDULER = JobScheduler()
