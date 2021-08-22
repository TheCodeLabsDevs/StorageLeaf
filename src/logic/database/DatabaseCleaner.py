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

    def __init__(self, retentionPolicies: List[RetentionPolicy], forceBackupAfterCleanup: bool):
        self._policies = retentionPolicies
        self._forceBackupAfterCleanup = forceBackupAfterCleanup

    def clean(self, db: Session, currentDate: datetime.date):
        LOGGER.info('Performing database cleanup...')

        for policy in self._policies:
            LOGGER.debug(f'Enforcing retention policy: {policy}')

            policyStart = currentDate - timedelta(days=policy.ageInDays)

            allSensors = Crud.get_sensors(db, skip=0, limit=1000000)
            for sensor in allSensors:
                LOGGER.debug(f'Cleaning measurements for sensor "{sensor.name}" '
                             f'(id: {sensor.id}, device_id: {sensor.device_id})')
                self._cleanup_measurements_for_sensor(sensor, db, policy, policyStart)

        LOGGER.info('Database cleanup done')

        if self._forceBackupAfterCleanup:
            Crud.BACKUP_SERVICE.backup()

    @staticmethod
    def _cleanup_measurements_for_sensor(sensor: Schemas.Sensor, db: Session,
                                         policy: RetentionPolicy, policyStart: datetime.date):
        firstMeasurement = Crud.get_first_measurement_for_sensor(db=db, sensorId=sensor.id)
        if firstMeasurement is None:
            return

        minDate = datetime.strptime(firstMeasurement.timestamp, Crud.DATE_FORMAT).date()

        processedDate = policyStart
        while processedDate > minDate:
            LOGGER.debug(f'Cleaning {processedDate.strftime("%Y-%m-%d")}...')
            DatabaseCleaner._cleanup_measurements_for_day(db, processedDate, policy, sensor.id)
            processedDate = processedDate - timedelta(days=1)

    @staticmethod
    def _cleanup_measurements_for_day(db: Session, date: datetime.date,
                                      policy: RetentionPolicy, sensor_id: int):
        measurementIds, idsToDelete = DatabaseCleaner._categorize_measurements_for_day(db,
                                                                                       date=date,
                                                                                       policy=policy,
                                                                                       sensorId=sensor_id)

        if not idsToDelete:
            return

        LOGGER.debug(f'Scheduled {len(idsToDelete)} measurements for deletion '
                     f'(keeping: {len(measurementIds)}, max allowed: {policy.numberOfMeasurementsPerDay})')
        Crud.delete_multiple_measurements(db, idsToDelete)

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
