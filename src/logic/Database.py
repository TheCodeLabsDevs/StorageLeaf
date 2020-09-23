import sqlite3
from datetime import datetime
from enum import Enum
from typing import Tuple, Dict

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
        self.__query(f'''CREATE TABLE IF NOT EXISTS sensor (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         device_id INTEGER,
                         name TEXT NOT NULL, 
                         type TEXT NOT NULL, 
                         value TEXT NOT NULL,
                         timestamp TEXT NOT NULL)''', fetch_type=FetchType.NONE)

    def __get_cursor(self):
        connection = sqlite3.connect(self._databasePath)
        connection.row_factory = Database.namedtuple_factory
        return connection.cursor()

    def __query(self, query, *args, fetch_type=FetchType.ALL):
        cursor = self.__get_cursor()
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

    def get_all_devices(self):
        return self.__query(f'SELECT * FROM {self.TABLE_DEVICE} ORDER BY name', fetch_type=FetchType.ALL)

    def get_device(self, deviceName: str):
        return self.__query(f'SELECT * FROM {self.TABLE_DEVICE} WHERE name = "{deviceName}"', fetch_type=FetchType.ONE)

    def add_device(self, deviceName: str):
        LOGGER.debug(f'Inserting new device "{deviceName}"')
        self.__query(f'INSERT INTO {self.TABLE_DEVICE}(name) VALUES(?)', deviceName, fetch_type=FetchType.NONE)

    def get_all_sensors(self):
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} ORDER BY device_id, name', fetch_type=FetchType.ALL)

    def get_sensor(self, deviceID: int, name: str):
        return self.__query(f'SELECT * FROM {self.TABLE_SENSOR} WHERE device_id = ? AND name = ?',
                            deviceID, name,
                            fetch_type=FetchType.ONE)

    def add_sensor(self, device: Dict[str, str], name: str, sensorType: str, value: str):
        LOGGER.debug(f'Inserting new sensor "{name}" for device "{device["name"]}" '
                     f'(type: "{sensorType}", value: "{value}")')
        self.__query(f'INSERT INTO {self.TABLE_SENSOR}(name, device_id, type, value, timestamp ) '
                     f'VALUES(?, ?, ?, ?, ?)',
                     name, device['id'], sensorType, value, self.__get_current_datetime(),
                     fetch_type=FetchType.NONE)

    def update_sensor(self, device: Dict[str, str], name: str, sensorType: str, value: str):
        LOGGER.debug(f'Updating sensor "{name}" for device "{device["name"]}" '
                     f'(type: "{sensorType}", value: "{value}")')
        self.__query(f'UPDATE {self.TABLE_SENSOR} SET value = ?, timestamp = ? '
                     f'WHERE device_id = ? AND name = ?',
                     value, self.__get_current_datetime(), device['id'], name,
                     fetch_type=FetchType.NONE)
