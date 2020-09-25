from enum import Enum

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants
from logic.DeviceAccess import DeviceAccess
from logic.MeasurementAccess import MeasurementAccess
from logic.SensorAccess import SensorAccess

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class Database:
    def __init__(self, databasePath):
        self._databasePath = databasePath
        self.deviceAccess = DeviceAccess(databasePath)
        self.sensorAccess = SensorAccess(databasePath)
        self.measurementAccess = MeasurementAccess(databasePath)

        self.__create_database()

    def __create_database(self):
        LOGGER.debug('Creating database tables...')
        self.deviceAccess.create_table()
        self.sensorAccess.create_table()
        self.measurementAccess.create_table()
