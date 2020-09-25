from datetime import datetime
from typing import Dict, List

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants
from logic.database.DatabaseAccess import DatabaseAccess, FetchType

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class MeasurementAccess(DatabaseAccess):
    TABLE_NAME = 'measurement'

    def create_table(self):
        self._query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         sensor_id INTEGER,
                         value TEXT NOT NULL,
                         timestamp TEXT NOT NULL)''', fetch_type=FetchType.NONE)

    def __get_current_datetime(self):
        return datetime.strftime(datetime.now(), self.DATE_FORMAT)

    def get_all_measurements(self) -> List[Dict[str, str]]:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} ORDER BY sensor_id ASC, datetime(timestamp) DESC',
                           fetch_type=FetchType.ALL)

    def get_measurement(self, measurementID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE id = ?',
                           measurementID,
                           fetch_type=FetchType.ALL)

    def get_all_measurements_for_sensor(self, sensorID: int) -> List[Dict[str, str]]:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? '
                           f'ORDER BY datetime(timestamp) DESC',
                           sensorID,
                           fetch_type=FetchType.ALL)

    def get_latest_measurements_for_sensor(self, sensorID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? '
                           f'ORDER BY datetime(timestamp) DESC LIMIT 1',
                           sensorID,
                           fetch_type=FetchType.ONE)

    def add_measurement(self, sensorID: int, value: str):
        LOGGER.debug(f'Inserting new measurement for sensor "{sensorID}" (value: "{value}")')
        self._query(f'INSERT INTO {self.TABLE_NAME}(sensor_id, value, timestamp ) VALUES(?, ?, ?)',
                    sensorID, value, self.__get_current_datetime(),
                    fetch_type=FetchType.NONE)

    def delete_measurement(self, measurementID: int):
        LOGGER.debug(f'Deleting measurement "{measurementID}"')
        self._query(f'DELETE FROM {self.TABLE_NAME} WHERE id = ?', measurementID, fetch_type=FetchType.NONE)

    def delete_measurements_for_sensor(self, sensorID: int):
        LOGGER.debug(f'Deleting all measurement for sensor "{sensorID}"')
        self._query(f'DELETE FROM {self.TABLE_NAME} WHERE sensor_id = ?', sensorID, fetch_type=FetchType.NONE)
