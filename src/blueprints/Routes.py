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
            database = Database(settings['database']['databasePath'])

            if not database.get_device(deviceName):
                database.add_device(deviceName)
            device = database.get_device(deviceName)

            sensors = parameters[DeviceParameters.SENSORS.value]
            for sensor in sensors:
                sensorParams = RequestValidator.validate_parameters(sensor,
                                                                    SensorParameters.get_values(),
                                                                    f'sensor "{sensor}"')
                __add_or_update_sensor(database, device, sensorParams)
        except ValidationError as e:
            return e.response, 400

        return ""

    def __add_or_update_sensor(database, device, sensorParams):
        sensorName = sensorParams[SensorParameters.NAME.value]
        sensorType = sensorParams[SensorParameters.TYPE.value]
        sensorValue = sensorParams[SensorParameters.VALUE.value]
        sensor = database.get_sensor(device[0], sensorName)
        if sensor:
            database.update_sensor(device, sensorName, sensorType, sensorValue)
        else:
            database.add_sensor(device, sensorName, sensorType, sensorValue)

    return routes
