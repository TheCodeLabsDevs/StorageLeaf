import json
import os
from enum import Enum
from typing import Dict

import yaml
from flask import Blueprint, request, jsonify, render_template

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

    @routes.route('/device/<int:deviceID>', methods=['GET'])
    def get_device(deviceID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_device(deviceID))

    @routes.route('/sensors', methods=['GET'])
    def get_all_sensors():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_all_sensors())

    @routes.route('/sensor/<int:sensorID>', methods=['GET'])
    def get_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_sensor(sensorID))

    @routes.route('/device/<int:deviceID>/sensors/', methods=['GET'])
    def get_all_sensors_for_device(deviceID):
        database = Database(settings['database']['databasePath'])
        device = database.get_device(deviceID)
        if not device:
            return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

        return jsonify(database.get_all_sensors_for_device(deviceID))

    @routes.route('/device/<deviceName>', methods=['POST'])
    def postSensorData(deviceName):
        try:
            parameters = RequestValidator.validate(request, DeviceParameters.get_values())
            database = Database(settings['database']['databasePath'])

            if not database.get_device_by_name(deviceName):
                database.add_device(deviceName)
            device = database.get_device_by_name(deviceName)

            sensors = parameters[DeviceParameters.SENSORS.value]
            for sensor in sensors:
                sensorParams = RequestValidator.validate_parameters(sensor,
                                                                    SensorParameters.get_values(),
                                                                    f'sensor "{sensor}"')
                sensor = __add_sensor_if_not_exists(database, int(device['id']), sensorParams)
                database.add_measurement(int(sensor['id']), sensorParams[SensorParameters.VALUE.value])
        except ValidationError as e:
            return e.response, 400

        return ""

    def __add_sensor_if_not_exists(database: Database, deviceID: int, sensorParams: Dict) -> Dict[str, str]:
        sensorName = sensorParams[SensorParameters.NAME.value]
        sensorType = sensorParams[SensorParameters.TYPE.value]
        sensor = database.get_sensor_by_name_and_device_id(deviceID, sensorName)
        if sensor:
            return sensor

        database.add_sensor(deviceID, sensorName, sensorType)
        return database.get_sensor_by_name_and_device_id(deviceID, sensorName)

    @routes.route('/measurements', methods=['GET'])
    def get_all_measurements():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_all_measurements())

    @routes.route('/measurement/<int:measurementID>', methods=['GET'])
    def get_measurement(measurementID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.get_measurement(measurementID))

    @routes.route('/sensor/<sensorID>/measurements', methods=['GET'])
    def get_all_measurements_for_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        sensor = database.get_sensor(sensorID)
        if not sensor:
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        return jsonify(database.get_all_measurements_for_sensor(sensorID))

    return routes
