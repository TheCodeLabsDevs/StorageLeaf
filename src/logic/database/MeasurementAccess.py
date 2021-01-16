import logging
from typing import Dict

from logic import Constants
from logic.database.DatabaseAccess import DatabaseAccess, FetchType

LOGGER = logging.getLogger(Constants.APP_NAME)


class MeasurementAccess(DatabaseAccess):
    def get_latest_measurements_for_sensor(self, sensorID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE sensor_id = ? '
                           f'ORDER BY datetime(timestamp) DESC LIMIT 1',
                           sensorID,
                           fetch_type=FetchType.ONE)
