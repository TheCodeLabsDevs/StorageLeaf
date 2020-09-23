import json
import os
from enum import Enum

import yaml
from flask import Blueprint, request, jsonify, send_from_directory, render_template

from logic import Constants
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


def construct_blueprint(settings, version):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        yamlPath = os.path.join(Constants.ROOT_DIR, 'docs', 'api.yml')
        with open(yamlPath, 'r') as yamlFile:
            specification = yaml.load(yamlFile, Loader=yaml.FullLoader)

        specification['servers'][0]['url'] = settings['api']['url']
        specification['info']['version'] = version['name']

        specification = json.dumps(specification)
        return render_template('api.html',
                               appName=Constants.APP_NAME,
                               openApiSpecification=specification)

    @routes.route('/devices', methods=['GET'])
    def get_all_devices():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_all_devices())

    @routes.route('/device/<deviceName>', methods=['GET'])
    def get_device(deviceName):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_device(deviceName))

    @routes.route('/sensors', methods=['GET'])
    def get_all_sensors():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_all_sensors())

    @routes.route('/device/<deviceName>/sensors/<sensorName>', methods=['GET'])
    def get_sensor(deviceName, sensorName):
        database = Database(settings['database']['databasePath'])
        device = database.get_device(deviceName)
        if not device:
            return jsonify({'success': False, 'msg': f'No device with name "{deviceName}" existing'})

        return jsonify(database.get_sensor(device['id'], sensorName))

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
        sensor = database.get_sensor(device['id'], sensorName)
        if sensor:
            database.update_sensor(device, sensorName, sensorType, sensorValue)
        else:
            database.add_sensor(device, sensorName, sensorType, sensorValue)

    return routes
