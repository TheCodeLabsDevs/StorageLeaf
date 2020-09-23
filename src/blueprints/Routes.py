from enum import Enum

from flask import Blueprint, request, jsonify

from logic.Database import Database
from logic.RequestValidator import ValidationError, RequestValidator


class DeviceParameters(Enum):
    SENSORS = 'sensors'

    @staticmethod
    def get_values():
        return [m.value for m in DeviceParameters]


class SensorParameters(Enum):
    NAME = 'name'
    TYPE = 'type'
    VALUE = 'value'

    @staticmethod
    def get_values():
        return [m.value for m in SensorParameters]


def construct_blueprint(settings):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        return "Hello World!"

    @routes.route('/device/<deviceName>', methods=['POST'])
    def postSensorData(deviceName):
        try:
            parameters = RequestValidator.validate(request, DeviceParameters.get_values())
            sensors = parameters[DeviceParameters.SENSORS.value]
            for sensor in sensors:
                sensorParams = RequestValidator.validate_parameters(sensor,
                                                                    SensorParameters.get_values(),
                                                                    f'sensor "{sensor}"')
                database = Database(settings['database']['databasePath'])
                database.add_device_if_not_exists(deviceName)
                device = database.get_device(deviceName)
                database.add_or_update_sensor(device,
                                              sensorParams['name'],
                                              sensorParams['type'],
                                              sensorParams['value'])
                return jsonify(database.get_device("0182"))

        except ValidationError as e:
            return e.response, 400

        return ""

    return routes
