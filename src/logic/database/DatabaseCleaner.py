import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Set

from sqlalchemy.orm import Session

from logic import Constants
from logic.database import Crud, Schemas
from logic.database.RetentionPolicy import RetentionPolicy

LOGGER = logging.getLogger(Constants.APP_NAME)


class DatabaseCleaner:
    MIN_DATE = datetime(year=1970, month=1, day=1).date()

    def __init__(self, retentionPolicies: List[RetentionPolicy]):
        self._policies = retentionPolicies

    def clean(self, db: Session, currentDate: datetime.date):
        LOGGER.info('Performing database cleanup...')

        for policy in self._policies:
            LOGGER.debug(f'Enforcing retention policy: {policy}')

            policyStart = currentDate - timedelta(days=policy.ageInDays)

            allSensors = Crud.get_sensors(db, skip=0, limit=1000000)
            for sensor in allSensors:
                LOGGER.debug(f'Cleaning measurements for sensor "{sensor.name}" '
                             f'(id: {sensor.id}, device_id: {sensor.device_id})')

                processedDate = policyStart
                while processedDate > self.MIN_DATE:
                    LOGGER.debug(f'Cleaning {processedDate.strftime("%Y-%m-%d")}...')
                    measurementIds, idsToDelete = DatabaseCleaner._categorize_measurements_for_day(db,
                                                                                                   date=processedDate,
                                                                                                   policy=policy,
                                                                                                   sensorId=sensor.id)

                    processedDate = processedDate - timedelta(days=1)

                    if not idsToDelete:
                        continue

                    LOGGER.debug(
                        f'Scheduled {len(idsToDelete)} measurements for deletion (keeping: {len(measurementIds)}, '
                        f'max allowed: {policy.numberOfMeasurementsPerDay})')

                    Crud.delete_multiple_measurements(db, idsToDelete)

        LOGGER.info('Database cleanup done')

        # TODO: force backup?

    @staticmethod
    def _categorize_measurements_for_day(db: Session, date: datetime.date,
                                         policy: RetentionPolicy, sensorId: int) -> Tuple[List[int], Set[int]]:
        points = policy.determine_measurement_points(date)

        measurementIdsToKeep = []
        allMeasurementIds = set()
        for index, point in enumerate(points):
            previousItem = DatabaseCleaner.__get_previous_item(index, point, points)
            nextItem = DatabaseCleaner.__get_next_item(index, point, points)

            possibleMeasurements = Crud.get_measurements_for_sensor(db, previousItem.strftime(Crud.DATE_FORMAT),
                                                                    nextItem.strftime(Crud.DATE_FORMAT), sensorId)

            allMeasurementIds.update([m.id for m in possibleMeasurements])

            closestMeasurement = DatabaseCleaner._get_closest_measurement_for_point(possibleMeasurements, point)
            if closestMeasurement is not None:
                measurementIdsToKeep.append(closestMeasurement.id)

        return measurementIdsToKeep, {m for m in allMeasurementIds if m not in measurementIdsToKeep}

    @staticmethod
    def __get_previous_item(index: int, point: datetime, points: List[datetime]) -> datetime:
        if index == 0:
            previousItem = point
        else:
            previousItem = points[index - 1]
        return previousItem

    @staticmethod
    def __get_next_item(index: int, point: datetime, points: List[datetime]) -> datetime:
        if index == (len(points) - 1):
            nextItem = datetime(year=point.year, month=point.month, day=point.day, hour=23, minute=59, second=59)
        else:
            nextItem = points[index + 1]
        return nextItem

    @staticmethod
    def _get_closest_measurement_for_point(measurements: List[Schemas.Measurement],
                                           point: datetime) -> Optional[Schemas.Measurement]:
        if not measurements:
            return None

        return min(measurements, key=lambda m: abs(datetime.strptime(m.timestamp, Crud.DATE_FORMAT) - point))
