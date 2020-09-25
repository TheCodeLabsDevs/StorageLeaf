import sqlite3
from datetime import datetime
from enum import Enum
from typing import Dict, List

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class FetchType(Enum):
    NONE = 1
    ONE = 2
    ALL = 3


class Database:
    TABLE_DEVICE = 'device'
    TABLE_SENSOR = 'sensor'
    TABLE_MEASUREMENT = 'measurement'

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def namedtuple_factory(cursor, row):
        """
        Returns sqlite rows as dicts.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __init__(self, databasePath):
        self._databasePath = databasePath
        self.__create_database()

    def __create_database(self):
        LOGGER.debug('Creating database tables...')
        self.__query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_DEVICE} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL)''', fetch_type=FetchType.NONE)
        self.__query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_SENSOR} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         device_id INTEGER,
                         name TEXT NOT NULL, 
                         type TEXT NOT NULL)''', fetch_type=FetchType.NONE)
        self.__query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_MEASUREMENT} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         sensor_id INTEGER,
                         value TEXT NOT NULL,
                         timestamp TEXT NOT NULL)''', fetch_type=FetchType.NONE)

    def __query(self, query, *args, fetch_type=FetchType.ALL):
        connection = sqlite3.connect(self._databasePath)
        connection.row_factory = Database.namedtuple_factory

        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, args)

                if fetch_type == FetchType.ONE:
                    return cursor.fetchone()
                if fetch_type == FetchType.ALL:
                    return cursor.fetchall()
            finally:
                cursor.close()

    def __get_current_datetime(self):
        return datetime.strftime(datetime.now(), self.DATE_FORMAT)

    def get_all_devices(self) -> List[Dict[str, str]]:
        return self.__query(f'SELECT * FROM {self.TABLE_DEVICE} ORDER BY name', fetch_type=FetchType.ALL)

    def get_device(self, deviceID: int) -> Dict[str, str] or None:
        return self.__query(f'SELECT * FROM {self.TABLE_DEVICE} WHERE id = ?', deviceID, fetch_type=FetchType.ONE)

    def get_device_by_name(self, deviceName: str) -> Dict[str, str] or None:
        return self.__query(f'SELECT * FROM {self.TABLE_DEVICE} WHERE name = ?', deviceName, fetch_type=FetchType.ONE)

    def add_device(self, deviceName: str):
        LOGGER.debug(f'Inserting new device "{deviceName}"')
        self.__query(f'INSERT INTO {self.TABLE_DEVICE}(name) VALUES(?)', deviceName, fetch_type=FetchType.NONE)

    def get_all_sensors(self) -> List[Dict[str, str]]:
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} ORDER BY device_id, name', fetch_type=FetchType.ALL)

    def get_all_sensors_for_device(self, deviceID: int) -> List[Dict[str, str]]:
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} WHERE device_id = ? ORDER BY name',
                            deviceID,
                            fetch_type=FetchType.ALL)

    def get_sensor(self, sensorID: int) -> Dict[str, str] or None:
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} WHERE id = ?',
                            sensorID,
                            fetch_type=FetchType.ONE)

    def get_sensor_by_name_and_device_id(self, deviceID: int, sensorName: str) -> Dict[str, str] or None:
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} WHERE device_id = ? AND name = ?',
                            deviceID, sensorName,
                            fetch_type=FetchType.ONE)

    def add_sensor(self, deviceID: int, name: str, sensorType: str):
        LOGGER.debug(f'Inserting new "{sensorType}" sensor "{name}" for device "{deviceID}"')
        self.__query(f'INSERT INTO {self.TABLE_SENSOR}(name, device_id, type) '
                     f'VALUES(?, ?, ?)',
                     name, deviceID, sensorType,
                     fetch_type=FetchType.NONE)

    def get_all_measurements(self) -> List[Dict[str, str]]:
        return self.__query(f'SELECT * FROM {self.TABLE_MEASUREMENT} ORDER BY sensor_id ASC, datetime(timestamp) DESC',
                            fetch_type=FetchType.ALL)

    def get_measurement(self, measurementID: int) -> Dict[str, str] or None:
        return self.__query(f'SELECT * FROM {self.TABLE_MEASUREMENT} WHERE id = ?',
                            measurementID,
                            fetch_type=FetchType.ALL)

    def get_all_measurements_for_sensor(self, sensorID: int) -> List[Dict[str, str]]:
        return self.__query(f'SELECT * FROM {self.TABLE_MEASUREMENT} WHERE sensor_id = ? '
                            f'ORDER BY datetime(timestamp) DESC',
                            sensorID,
                            fetch_type=FetchType.ALL)

    def add_measurement(self, sensorID: int, value: str):
        sensor = self.get_sensor(sensorID)
        LOGGER.debug(f'Inserting new measurement for sensor "{sensor["name"]}" '
                     f'(value: "{value}", device_id "{sensor["device_id"]}")')
        self.__query(f'INSERT INTO {self.TABLE_MEASUREMENT}(sensor_id, value, timestamp ) VALUES(?, ?, ?)',
                     sensorID, value, self.__get_current_datetime(),
                     fetch_type=FetchType.NONE)
