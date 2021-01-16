import logging
from datetime import datetime
from typing import Dict, List

from logic import Constants
from logic.database.DatabaseAccess import DatabaseAccess, FetchType

LOGGER = logging.getLogger(Constants.APP_NAME)


class MeasurementAccess(DatabaseAccess):
    TABLE_NAME = 'measurement'

    def create_table(self):
        self._query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         sensor_id INTEGER,
                         value TEXT NOT NULL,
                         timestamp TEXT NOT NULL)''', fetch_type=FetchType.CREATE)

    def __get_current_datetime(self):
        return datetime.strftime(datetime.now(), self.DATE_FORMAT)

    def get_all_measurements(self, startDateTime: str, endDateTime: str) -> List[Dict[str, str]]:
        if startDateTime and endDateTime:
            return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE '
                               f'DATETIME(timestamp) BETWEEN DATETIME(?) AND DATETIME(?) '
                               f'ORDER BY sensor_id ASC, datetime(timestamp) DESC',
                               startDateTime,
                               endDateTime,
                               fetch_type=FetchType.ALL)

        return self._query(f'SELECT * FROM {self.TABLE_NAME} ORDER BY sensor_id ASC, '
                           f'datetime(timestamp) DESC',
                           fetch_type=FetchType.ALL)

    def get_all_measurements_for_sensor(self, sensorID: int,
                                        startDateTime: str,
                                        endDateTime: str) -> List[Dict[str, str]]:
        if startDateTime and endDateTime:
            return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? '
                               f'AND DATETIME(timestamp) BETWEEN DATETIME(?) AND DATETIME(?) '
                               f'ORDER BY datetime(timestamp) DESC',
                               sensorID,
                               startDateTime,
                               endDateTime,
                               fetch_type=FetchType.ALL)

        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? ORDER BY datetime(timestamp) DESC',
                           sensorID,
                           fetch_type=FetchType.ALL)

    def get_latest_measurements_for_sensor(self, sensorID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? '
                           f'ORDER BY datetime(timestamp) DESC LIMIT 1',
                           sensorID,
                           fetch_type=FetchType.ONE)

