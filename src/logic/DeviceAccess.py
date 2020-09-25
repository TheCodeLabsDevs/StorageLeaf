from typing import Dict, List

from TheCodeLabs_BaseUtils import DefaultLogger

from logic import Constants
from logic.DatabaseAccess import DatabaseAccess, FetchType

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class DeviceAccess(DatabaseAccess):
    TABLE_NAME = 'device'

    def create_table(self):
        self._query(f'''CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL)''', fetch_type=FetchType.NONE)

    def get_all_devices(self) -> List[Dict[str, str]]:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} ORDER BY name', fetch_type=FetchType.ALL)

    def get_device(self, deviceID: int) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE id = ?', deviceID, fetch_type=FetchType.ONE)

    def get_device_by_name(self, deviceName: str) -> Dict[str, str] or None:
        return self._query(f'SELECT * FROM {self.TABLE_NAME} WHERE name = ?', deviceName, fetch_type=FetchType.ONE)

    def add_device(self, deviceName: str):
        LOGGER.debug(f'Inserting new device "{deviceName}"')
        self._query(f'INSERT INTO {self.TABLE_NAME}(name) VALUES(?)', deviceName, fetch_type=FetchType.NONE)
