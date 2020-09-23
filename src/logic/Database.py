import sqlite3
from typing import Tuple

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class Database:
    TABLE_DEVICE = 'device'
    TABLE_SENSOR = 'sensor'

    def __init__(self, databasePath):
        self._databasePath = databasePath
        self.__create_database()

    def __create_database(self):
        LOGGER.debug('Creating database tables...')
        with self.__get_connection() as connection:
            connection.execute(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_DEVICE} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL)''')
            connection.execute(f'''CREATE TABLE IF NOT EXISTS sensor (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         device_id INTEGER,
                         name TEXT NOT NULL, 
                         type TEXT NOT NULL, 
                         value TEXT NOT NULL)''')

    def __get_connection(self):
        return sqlite3.connect(self._databasePath)

    def get_all_devices(self):
        with self.__get_connection() as connection:
            cursor = connection.execute(f'SELECT * FROM {self.TABLE_DEVICE} ORDER BY name')
            return cursor.fetchall()

    def get_device(self, deviceName: str):
        with self.__get_connection() as connection:
            cursor = connection.execute(f'SELECT * FROM {self.TABLE_DEVICE} WHERE name = "{deviceName}"')
            return cursor.fetchone()

    def add_device_if_not_exists(self, deviceName: str):
        if self.get_device(deviceName):
            LOGGER.debug(f'Device "{deviceName}" already exists')
            return

        with self.__get_connection() as connection:
            LOGGER.debug(f'Inserting new device "{deviceName}"')
            connection.execute(f'INSERT INTO {self.TABLE_DEVICE}(name) VALUES(?)', (deviceName,))

    def get_all_sensors(self):
        with self.__get_connection() as connection:
            cursor = connection.execute(f'SELECT * FROM {self.TABLE_SENSOR} ORDER BY device_id, name')
            return cursor.fetchall()

    def get_sensor(self, deviceName: str, name: str):
        device = self.get_device(deviceName)
        if not device:
            return None

        with self.__get_connection() as connection:
            cursor = connection.execute(f'SELECT * FROM {self.TABLE_SENSOR} WHERE device_id = ? AND name = ?',
                                        (device[0], name))
            return cursor.fetchone()

    def add_or_update_sensor(self, device: Tuple[int, str], name: str, sensorType: str, value: str):
        sensor = self.get_sensor(device[1], name)
        with self.__get_connection() as connection:
            if sensor:
                LOGGER.debug(f'Updating sensor "{name}" for device "{device[1]}" (type: "{sensorType}", value: "{value}")')
                connection.execute(f'UPDATE {self.TABLE_SENSOR} SET value = ? WHERE device_id = ? AND name = ?',
                                   (value, device[0], name))
            else:
                LOGGER.debug(f'Inserting new sensor "{name}" for device "{device[1]}" (type: "{sensorType}", value: "{value}")')
                connection.execute(f'INSERT INTO {self.TABLE_SENSOR}(name, device_id, type, value) VALUES(?, ?, ?, ?)',
                                   (name, device[0], sensorType, value))
