from typing import Dict, List

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants
from logic.database.DatabaseAccess import DatabaseAccess, FetchType

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class SensorAccess(DatabaseAccess):
    TABLE_NAME = 'sensor'

    def create_table(self):
        self._query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         device_id INTEGER,
                         name TEXT NOT NULL, 
                         type TEXT NOT NULL)''', fetch_type=FetchType.NONE)

    def get_all_sensors(self) -> List[Dict[str, str]]:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} ORDER BY device_id, name', fetch_type=FetchType.ALL)

    def get_all_sensors_for_device(self, deviceID: int) -> List[Dict[str, str]]:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE device_id = ? ORDER BY name',
                           deviceID,
                           fetch_type=FetchType.ALL)

    def get_sensor(self, sensorID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE id = ?',
                           sensorID,
                           fetch_type=FetchType.ONE)

    def get_sensor_by_name_and_device_id(self, deviceID: int, sensorName: str) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE device_id = ? AND name = ?',
                           deviceID, sensorName,
                           fetch_type=FetchType.ONE)

    def add_sensor(self, deviceID: int, name: str, sensorType: str):
        LOGGER.debug(f'Inserting new "{sensorType}" sensor "{name}" for device "{deviceID}"')
        self._query(f'INSERT INTO {self.TABLE_NAME}(name, device_id, type) '
                    f'VALUES(?, ?, ?)',
                    name, deviceID, sensorType,
                    fetch_type=FetchType.NONE)
