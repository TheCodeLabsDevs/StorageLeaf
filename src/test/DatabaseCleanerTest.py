import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger

from logic import Constants
from logic.database import Schemas
from logic.database.RetentionPolicy import RetentionPolicy

CURRENT_DATE_TIME = datetime(year=2021, month=8, day=18, hour=22, minute=0, second=0)
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class TestRetentionPolicy(unittest.TestCase):
    def test_determineMeasurementPoints_oddNumberOfPoints_raise(self):
        policy = RetentionPolicy(1, 10)

        with self.assertRaises(ValueError):
            policy.determine_measurement_points(CURRENT_DATE_TIME.date())

    def test_determineMeasurementPoints_zero_raise(self):
        policy = RetentionPolicy(0, 10)

        with self.assertRaises(ValueError):
            policy.determine_measurement_points(CURRENT_DATE_TIME.date())

    def test_determineMeasurementPoints_twoPoints(self):
        policy = RetentionPolicy(2, 10)

        expected = [
            datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=12, minute=0, second=0)
        ]

        self.assertEqual(expected, policy.determine_measurement_points(CURRENT_DATE_TIME.date()))

    def test_determineMeasurementPoints_fourPoints(self):
        policy = RetentionPolicy(4, 10)

        expected = [
            datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=6, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=12, minute=0, second=0),
            datetime(year=2021, month=8, day=18, hour=18, minute=0, second=0),
        ]

        self.assertEqual(expected, policy.determine_measurement_points(CURRENT_DATE_TIME.date()))

    def test_determineMeasurementPoints_moreThan24Hours(self):
        policy = RetentionPolicy(30, 10)

        result = policy.determine_measurement_points(CURRENT_DATE_TIME.date())
        self.assertEqual(30, len(result))
        self.assertIn(datetime(year=2021, month=8, day=18, hour=0, minute=0, second=0), result)
        self.assertIn(datetime(year=2021, month=8, day=18, hour=0, minute=48, second=0), result)


class TestDatabaseCleaner(unittest.TestCase):
    MEASUREMENT1 = Schemas.Measurement(id=1, value=5, sensor_id=1,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=6, minute=55, second=0).strftime(DATE_FORMAT))
    MEASUREMENT2 = Schemas.Measurement(id=2, value=5, sensor_id=1,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=13, minute=15, second=0).strftime(DATE_FORMAT))

    MEASUREMENT3 = Schemas.Measurement(id=3, value=5, sensor_id=1,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=13, minute=45, second=0).strftime(DATE_FORMAT))

    MEASUREMENT4 = Schemas.Measurement(id=4, value=5, sensor_id=1,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=13, minute=48, second=0).strftime(DATE_FORMAT))

    MEASUREMENT5 = Schemas.Measurement(id=5, value=5, sensor_id=2,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=11, minute=55, second=0).strftime(DATE_FORMAT))

    MEASUREMENT6 = Schemas.Measurement(id=6, value=5, sensor_id=2,
                                       timestamp=datetime(year=2021, month=8, day=18,
                                                          hour=11, minute=54, second=0).strftime(DATE_FORMAT))

    @classmethod
    def get_measurements_mocked(cls, db, startTime, endTime, sensorId):
        if sensorId == 1:
            if startTime == '2021-08-18 00:00:00' and endTime == '2021-08-18 06:00:00':
                return [cls.MEASUREMENT1]
            if startTime == '2021-08-18 00:00:00' and endTime == '2021-08-18 12:00:00':
                return [cls.MEASUREMENT1]
            elif startTime == '2021-08-18 06:00:00' and endTime == '2021-08-18 18:00:00':
                return [cls.MEASUREMENT1, cls.MEASUREMENT2, cls.MEASUREMENT3, cls.MEASUREMENT4]
            elif startTime == '2021-08-18 12:00:00' and endTime == '2021-08-18 23:59:59':
                return [cls.MEASUREMENT2, cls.MEASUREMENT3, cls.MEASUREMENT4]
            elif startTime == '2021-08-18 18:00:00' and endTime == '2021-08-18 23:59:59':
                return []
            else:
                return []
        else:
            if startTime == '2021-08-18 00:00:00' and endTime == '2021-08-18 12:00:00':
                return [cls.MEASUREMENT5, cls.MEASUREMENT6]
            else:
                return []

    def test__GetClosestMeasurementForPoint_noMeasurementInRange(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            from logic.database.DatabaseCleaner import DatabaseCleaner

            result = DatabaseCleaner._get_closest_measurement_for_point([], CURRENT_DATE_TIME)
            self.assertIsNone(result)

    def test__GetClosestMeasurementForPoint_getClosest_AllMeasurementsBeforePoint(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = DATE_FORMAT

            from logic.database.DatabaseCleaner import DatabaseCleaner

            expected = Schemas.Measurement(id=2, value=5, sensor_id=15,
                                           timestamp=datetime(year=2021, month=8, day=18,
                                                              hour=21, minute=55, second=0).strftime(DATE_FORMAT))
            measurements = [
                Schemas.Measurement(id=1, value=5, sensor_id=15,
                                    timestamp=datetime(year=2021, month=8, day=18,
                                                       hour=21, minute=50, second=0).strftime(DATE_FORMAT)),
                expected
            ]

            result = DatabaseCleaner._get_closest_measurement_for_point(measurements, CURRENT_DATE_TIME)
            self.assertEqual(expected, result)

    def test__GetClosestMeasurementForPoint_getClosest_AllMeasurementsAfterPoint(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = DATE_FORMAT

            from logic.database.DatabaseCleaner import DatabaseCleaner

            expected = Schemas.Measurement(id=1, value=5, sensor_id=15,
                                           timestamp=datetime(year=2021, month=8, day=18,
                                                              hour=22, minute=15, second=0).strftime(DATE_FORMAT))
            measurements = [
                expected,
                Schemas.Measurement(id=1, value=5, sensor_id=15,
                                    timestamp=datetime(year=2021, month=8, day=18,
                                                       hour=22, minute=30, second=0).strftime(DATE_FORMAT))
            ]

            result = DatabaseCleaner._get_closest_measurement_for_point(measurements, CURRENT_DATE_TIME)
            self.assertEqual(expected, result)

    def test__GetClosestMeasurementForPoint_getClosest_BothSidesOfPoint(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = DATE_FORMAT

            from logic.database.DatabaseCleaner import DatabaseCleaner

            expected = Schemas.Measurement(id=1, value=5, sensor_id=15,
                                           timestamp=datetime(year=2021, month=8, day=18,
                                                              hour=21, minute=55, second=0).strftime(DATE_FORMAT))
            measurements = [
                expected,
                Schemas.Measurement(id=1, value=5, sensor_id=15,
                                    timestamp=datetime(year=2021, month=8, day=18,
                                                       hour=22, minute=10, second=0).strftime(DATE_FORMAT))
            ]

            result = DatabaseCleaner._get_closest_measurement_for_point(measurements, CURRENT_DATE_TIME)
            self.assertEqual(expected, result)

    def test__GetClosestMeasurementForPoint_getClosest_EqualDistance(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = DATE_FORMAT

            from logic.database.DatabaseCleaner import DatabaseCleaner

            expected = Schemas.Measurement(id=1, value=5, sensor_id=15,
                                           timestamp=datetime(year=2021, month=8, day=18,
                                                              hour=21, minute=55, second=0).strftime(DATE_FORMAT))
            measurements = [
                expected,
                Schemas.Measurement(id=1, value=5, sensor_id=15,
                                    timestamp=datetime(year=2021, month=8, day=18,
                                                       hour=22, minute=5, second=0).strftime(DATE_FORMAT))
            ]

            result = DatabaseCleaner._get_closest_measurement_for_point(measurements, CURRENT_DATE_TIME)
            self.assertEqual(expected, result)

    def test_GetMeasurementsForDay(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = DATE_FORMAT
            mockedCrud.get_measurements_for_sensor.side_effect = self.get_measurements_mocked

            from logic.database.DatabaseCleaner import DatabaseCleaner

            database = Mock()
            policy = RetentionPolicy(numberOfMeasurementsPerDay=4, ageInDays=10)
            measurementIds, idsToDelete = DatabaseCleaner._categorize_measurements_for_day(database,
                                                                                           CURRENT_DATE_TIME.date(),
                                                                                           policy, 1)
            self.assertEqual([self.MEASUREMENT1.id, self.MEASUREMENT1.id, self.MEASUREMENT2.id, self.MEASUREMENT4.id],
                             measurementIds)
            self.assertEqual({self.MEASUREMENT3.id}, idsToDelete)

    def test_noRetentionPolicies_doNothing(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.get_measurements_for_sensor.return_value = []

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            DatabaseCleaner([]).clean(database, CURRENT_DATE_TIME)

            mockedCrud.get_measurements_for_sensor.assert_not_called()

    def test_onePolicy_deleteMeasurements_oneSensor(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
            mockedCrud.get_measurements_for_sensor.side_effect = self.get_measurements_mocked
            mockedCrud.get_sensors.return_value = [Schemas.Sensor(id=1, name="myTempSensor",
                                                                  type="temperature", device_id=1)]

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            from logic.database.DatabaseCleaner import RetentionPolicy

            policy = RetentionPolicy(numberOfMeasurementsPerDay=4, ageInDays=1)
            DatabaseCleaner([policy]).clean(database, datetime(year=2021, month=8, day=19).date())

            mockedCrud.delete_multiple_measurements.assert_called_once_with(database, {3})

    def test_onePolicy_deleteMeasurements_twoSensors(self):
        mockedCrud = Mock()
        with patch.dict('sys.modules', **{'logic.database.Crud': mockedCrud}):
            mockedCrud.DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
            mockedCrud.get_measurements_for_sensor.side_effect = self.get_measurements_mocked
            mockedCrud.get_sensors.return_value = [Schemas.Sensor(id=1, name="myTempSensor",
                                                                  type="temperature", device_id=1),
                                                   Schemas.Sensor(id=2, name="myHumiditySensor",
                                                                  type="humidity", device_id=1)]

            database = Mock()
            from logic.database.DatabaseCleaner import DatabaseCleaner
            from logic.database.DatabaseCleaner import RetentionPolicy

            policy = RetentionPolicy(numberOfMeasurementsPerDay=4, ageInDays=1)
            DatabaseCleaner([policy]).clean(database, datetime(year=2021, month=8, day=19).date())

            calls = mockedCrud.delete_multiple_measurements.call_args_list
            self.assertEqual(2, len(calls))
            self.assertEqual((database, {3}), calls[0].args)
            self.assertEqual((database, {5}), calls[1].args)


            # TODO: test: multiple policies
