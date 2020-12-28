import os

from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from TheCodeLabs_FlaskUtils.FlaskBaseApp import FlaskBaseApp

from blueprints import Routes, Devices, Sensors, Measurements
from logic import Constants
from logic.BackupService import BackupService
from logic.DiscoveryService import DiscoveryService

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class StorageLeaf(FlaskBaseApp):
    def __init__(self, appName: str):
        super().__init__(appName, os.path.dirname(__file__), LOGGER, serveRobotsTxt=False)
        databaseSettings = self._settings['database']
        self._backupService = BackupService(databaseSettings['databasePath'], **databaseSettings['backup'])

        discoverySettings = self._settings['discovery']
        discoverySettings['apiPort'] = self._settings['server']['port']
        self._discoveryService = DiscoveryService(**discoverySettings)
        self._discoveryService.start()

    def _register_blueprints(self, app):
        app.register_blueprint(Routes.construct_blueprint(self._settings, self._version))
        app.register_blueprint(Devices.construct_blueprint(self._settings, self._backupService))
        app.register_blueprint(Sensors.construct_blueprint(self._settings, self._backupService))
        app.register_blueprint(Measurements.construct_blueprint(self._settings, self._backupService))
        return app


if __name__ == '__main__':
    website = StorageLeaf(Constants.APP_NAME)
    website.start_server()
