import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from logic.database.RetentionPolicy import RetentionPolicy

CURRENT_DATE_TIME = datetime(year=2021, month=8, day=18, hour=22, minute=0, second=0)


class TestRetentionPolicy(unittest.TestCase):
    def test_determineMeasurementPoints_oddNumberOfPoints_raise(self):
        policy = RetentionPolicy(1, 10)

        with self.assertRaises(ValueError):
            policy.determine_measurement_points(CURRENT_DATE_TIME)

    def test_determineMeasurementPoints_zero_raise(self):
        policy = RetentionPolicy(0, 10)

        with self.assertRaises(ValueError):
            policy.determine_measurement_points(CURRENT_DATE_TIME)

    def test_determineMeasurementPoints_twoPoints(self):
        policy = RetentionPolicy(2, 10)

        expected = [
            datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=12, minute=0, second=0)
        ]

        self.assertEqual(expected, policy.determine_measurement_points(CURRENT_DATE_TIME))

    def test_determineMeasurementPoints_fourPoints(self):
        policy = RetentionPolicy(4, 10)

        expected = [
            datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=6, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=12, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=18, minute=0, second=0),
        ]

        self.assertEqual(expected, policy.determine_measurement_points(CURRENT_DATE_TIME))

    def test_determineMeasurementPoints_moreThan24Hours(self):
        policy = RetentionPolicy(30, 10)

        result = policy.determine_measurement_points(CURRENT_DATE_TIME)
        self.assertEqual(30, len(result))
        self.assertIn(datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0), result)
        self.assertIn(datetime(year=2021, month=8, day=18, hour=0, minute=48, second=0), result)


class TestDatabaseCleaner(unittest.TestCase):
    def test_getMeasurementsByDay(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.get_measurements.return_value = []
            mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            DatabaseCleaner([])._get_measurements_by_day(database, CURRENT_DATE_TIME)

            mockedCrud.get_measurements.assert_called_once_with(db=database,
                                                                startDateTime='2021-08-18 00:00:00',
                                                                endDateTime='2021-08-18 23:59:59')

    # def test_noRetentionPolicies_doNothing(self):
    #     mockedCrud = Mock()
    #     with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
    #         mockedCrud.get_measurements.return_value = []
    #
    #         database = Mock()
    #         from logic.database.DatabaseCleaner import DatabaseCleaner
    #         DatabaseCleaner([]).clean(database, CURRENT_DATE_TIME)
    #
    #         mockedCrud.get_measurements.assert_not_called()
    #
    # def test_onePolicy_fetchMeasurementsOlderThanPolicyStart(self):
    #     mockedCrud = Mock()
    #     with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
    #         mockedCrud.get_measurements.return_value = []
    #         mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    #
    #         database = Mock()
    #         from logic.database.DatabaseCleaner import DatabaseCleaner
    #         from logic.database.DatabaseCleaner import RetentionPolicy
    #
    #         policy = RetentionPolicy(numberOfMeasurementsPerDay=4, ageInDays=1)
    #         DatabaseCleaner([policy]).clean(database, CURRENT_DATE_TIME)
    #
    #         expectedEndTime = CURRENT_DATE_TIME - timedelta(days=policy.ageInDays)
    #         mockedCrud.get_measurements.assert_called_once_with(db=database,
    #                                                             startDateTime=DatabaseCleaner.MIN_DATETIME.strftime(mockedCrud.DATE_FORMAT),
    #                                                             endDateTime=expectedEndTime.strftime(mockedCrud.DATE_FORMAT))
    #
    # def test_onePolicy_deleteMeasurements(self):
    #     mockedCrud = Mock()
    #     with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
    #
    #         measurementToBeDeleted1 = Schemas.Measurement(id=1, value='5', timestamp='2021-08-17 20:05:00', sensor_id=2)
    #         measurementToKeep = Schemas.Measurement(id=2, value='5', timestamp='2021-08-17 20:09:12', sensor_id=2)
    #         measurementToBeDeleted2 = Schemas.Measurement(id=3, value='5', timestamp='2021-08-17 21:07:12', sensor_id=2)
    #         measurementToBeDeleted3 = Schemas.Measurement(id=4, value='5', timestamp='2021-08-17 21:09:12', sensor_id=2)
    #         measurementAfterPolicyStart = Schemas.Measurement(id=5, value='5', timestamp='2021-08-17 21:10:12', sensor_id=2)
    #
    #         mockedCrud.get_measurements.return_value = [measurementToBeDeleted1, measurementToKeep, measurementToBeDeleted2, measurementToBeDeleted3, measurementAfterPolicyStart]
    #         mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    #
    #         database = Mock()
    #         from logic.database.DatabaseCleaner import DatabaseCleaner
    #         from logic.database.DatabaseCleaner import RetentionPolicy
    #
    #         policy = RetentionPolicy(resolutionInMinutes=10, ageInDays=1)
    #         DatabaseCleaner([policy]).clean(database, self.CURRENT_DATE_TIME)
    #
    #         mockedCrud.delete_multiple_measurements.assert_called_once_with(database, [4, 3, 1])
    #
    # # TODO: test: if cleanup is performed on the next day: prevent deletion of already low resolution measurements
