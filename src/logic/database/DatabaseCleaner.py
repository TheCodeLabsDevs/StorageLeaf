import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from logic import Constants
from logic.database import Crud, Schemas
from logic.database.RetentionPolicy import RetentionPolicy

LOGGER = logging.getLogger(Constants.APP_NAME)


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

    @staticmethod
    def _get_measurements_by_day(db: Session, date: datetime.date) -> List[Schemas.Measurement]:
        startTime = datetime(year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0, microsecond=0)
        endTime = datetime(year=date.year, month=date.month, day=date.day, hour=23, minute=59, second=59, microsecond=0)

        return Crud.get_measurements(db=db,
                                     startDateTime=startTime.strftime(Crud.DATE_FORMAT),
                                     endDateTime=endTime.strftime(Crud.DATE_FORMAT))

    def _get_closest_measurement_for_point(self, measurements: List[Schemas.Measurement],
                                           point: datetime,
                                           upperLimit: datetime,
                                           lowerLimit: datetime) -> Optional[Schemas.Measurement]:
        pass

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

        LOGGER.debug(
            f'Scheduled {len(measurementsIdsToDelete)} measurements for deletion (keeping {len(affectedMeasurements) - len(measurementsIdsToDelete)})')
        Crud.delete_multiple_measurements(db, measurementsIdsToDelete)
