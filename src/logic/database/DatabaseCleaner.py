import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from logic import Constants
from logic.database import Crud

LOGGER = logging.getLogger(Constants.APP_NAME)


@dataclass
class RetentionPolicy:
    resolutionInMinutes: int
    ageInDays: int


class DatabaseCleaner:
    MIN_DATETIME = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # TODO DEBUG:
    # MIN_DATETIME = datetime.now() - timedelta(days=31)

    def __init__(self, retentionPolicies: List[RetentionPolicy]):
        self._policies = retentionPolicies

    def clean(self, db: Session, currentDateTime: datetime):
        LOGGER.info('Performing database cleanup...')

        for policy in self._policies:
            LOGGER.debug(f'Enforcing retention policy: {policy}')

            policyStart = currentDateTime - timedelta(days=policy.ageInDays)

            affectedMeasurements = Crud.get_measurements(db=db,
                                                         startDateTime=self.MIN_DATETIME.strftime(Crud.DATE_FORMAT),
                                                         endDateTime=policyStart.strftime(Crud.DATE_FORMAT))
            LOGGER.debug(f'Found {len(affectedMeasurements)} measurements older than {policyStart}')
            if not affectedMeasurements:
                continue

            affectedMeasurements.reverse()

            self.__delete_old_measurements(affectedMeasurements, db, policy)

        LOGGER.info('Database cleanup done')

        # TODO: force backup?

    def __delete_old_measurements(self, affectedMeasurements, db, policy):
        lastTimestamp = datetime.strptime(affectedMeasurements[0].timestamp, Crud.DATE_FORMAT)
        nextAllowedTimestamp = lastTimestamp - timedelta(minutes=policy.resolutionInMinutes)

        measurementsIdsToDelete = []

        for measurement in affectedMeasurements[1:]:
            timestamp = datetime.strptime(measurement.timestamp, Crud.DATE_FORMAT)
            if timestamp > nextAllowedTimestamp:
                measurementsIdsToDelete.append(measurement.id)
            else:
                lastTimestamp = timestamp
                nextAllowedTimestamp = lastTimestamp - timedelta(minutes=policy.resolutionInMinutes)

        LOGGER.debug(f'Scheduled {len(measurementsIdsToDelete)} measurements for deletion (keeping {len(affectedMeasurements) - len(measurementsIdsToDelete)})')
        Crud.delete_multiple_measurements(db, measurementsIdsToDelete)
