import os

from TheCodeLabs_BaseUtils.DefaultLogger import DefaultLogger
from TheCodeLabs_FlaskUtils.FlaskBaseApp import FlaskBaseApp

from blueprints import Routes
from logic import Constants

LOGGER = DefaultLogger().create_logger_if_not_exists(Constants.APP_NAME)


class StorageLeaf(FlaskBaseApp):
    def __init__(self, appName: str):
        super().__init__(appName, os.path.dirname(__file__), LOGGER, serveRobotsTxt=False)

    def _register_blueprints(self, app):
        app.register_blueprint(Routes.construct_blueprint(self._settings))
        return app


if __name__ == '__main__':
    website = StorageLeaf(Constants.APP_NAME)
    website.start_server()
