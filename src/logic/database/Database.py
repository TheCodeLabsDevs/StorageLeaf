import logging

from logic import Constants
from logic.database.DeviceAccess import DeviceAccess
from logic.database.MeasurementAccess import MeasurementAccess
from logic.database.SensorAccess import SensorAccess

LOGGER = logging.getLogger(Constants.APP_NAME)


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
