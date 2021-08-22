import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from logic.database import Schemas


class TestDatabaseCleaner(unittest.TestCase):
    CURRENT_DATE_TIME = datetime(year=2021, month=8, day=18, hour=22, minute=0, second=0)

    def test_noRetentionPolicies_doNothing(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.get_measurements.return_value = []

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            DatabaseCleaner([]).clean(database, self.CURRENT_DATE_TIME)

            mockedCrud.get_measurements.assert_not_called()

    def test_onePolicy_fetchMeasurementsOlderThanPolicyStart(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.get_measurements.return_value = []
            mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            from logic.database.DatabaseCleaner import RetentionPolicy

            policy = RetentionPolicy(resolutionInMinutes=10, ageInDays=1)
            DatabaseCleaner([policy]).clean(database, self.CURRENT_DATE_TIME)

            expectedEndTime = self.CURRENT_DATE_TIME - timedelta(days=policy.ageInDays)
            mockedCrud.get_measurements.assert_called_once_with(db=database,
                                                                startDateTime=DatabaseCleaner.MIN_DATETIME.strftime(mockedCrud.DATE_FORMAT),
                                                                endDateTime=expectedEndTime.strftime(mockedCrud.DATE_FORMAT))

    def test_onePolicy_deleteMeasurements(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):

            measurementToBeDeleted1 = Schemas.Measurement(id=1, value='5', timestamp='2021-08-17 20:05:00', sensor_id=2)
            measurementToKeep = Schemas.Measurement(id=2, value='5', timestamp='2021-08-17 20:09:12', sensor_id=2)
            measurementToBeDeleted2 = Schemas.Measurement(id=3, value='5', timestamp='2021-08-17 21:07:12', sensor_id=2)
            measurementToBeDeleted3 = Schemas.Measurement(id=4, value='5', timestamp='2021-08-17 21:09:12', sensor_id=2)
            measurementAfterPolicyStart = Schemas.Measurement(id=5, value='5', timestamp='2021-08-17 21:10:12', sensor_id=2)

            mockedCrud.get_measurements.return_value = [measurementToBeDeleted1, measurementToKeep, measurementToBeDeleted2, measurementToBeDeleted3, measurementAfterPolicyStart]
            mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            from logic.database.DatabaseCleaner import RetentionPolicy

            policy = RetentionPolicy(resolutionInMinutes=10, ageInDays=1)
            DatabaseCleaner([policy]).clean(database, self.CURRENT_DATE_TIME)

            mockedCrud.delete_multiple_measurements.assert_called_once_with(database, [4, 3, 1])

    # TODO: test: if cleanup is performed on the next day: prevent deletion of already low resolution measurements
