import json
import os
from enum import Enum
from typing import Dict

import yaml
from flask import Blueprint, request, jsonify, render_template

from logic import Constants
from logic.AuthenticationWrapper import require_api_key
from logic.Database import Database
from logic.RequestValidator import ValidationError, RequestValidator


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

    @routes.route('/measurements', methods=['GET'])
    def get_all_measurements():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.measurementAccess.get_all_measurements())

    @routes.route('/measurement/<int:measurementID>', methods=['GET'])
    def get_measurement(measurementID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.measurementAccess.get_measurement(measurementID))

    @routes.route('/measurements', methods=['POST'])
    @require_api_key(password=settings['api']['key'])
    def addMeasurement():
        try:
            parameters = RequestValidator.validate(request, DeviceParameters.get_values())
            database = Database(settings['database']['databasePath'])

            deviceName = parameters[DeviceParameters.DEVICE.value]
            if not database.deviceAccess.get_device_by_name(deviceName):
                database.deviceAccess.add_device(deviceName)
            device = database.deviceAccess.get_device_by_name(deviceName)

            sensors = parameters[DeviceParameters.SENSORS.value]
            for sensor in sensors:
                sensorParams = RequestValidator.validate_parameters(sensor,
                                                                    SensorParameters.get_values(),
                                                                    f'sensor "{sensor}"')
                sensor = __add_sensor_if_not_exists(database, int(device['id']), sensorParams)
                database.measurementAccess.add_measurement(int(sensor['id']),
                                                           sensorParams[SensorParameters.VALUE.value])
        except ValidationError as e:
            return e.response, 400

        return jsonify({'success': True})

    def __add_sensor_if_not_exists(database: Database, deviceID: int, sensorParams: Dict) -> Dict[str, str]:
        sensorName = sensorParams[SensorParameters.NAME.value]
        sensorType = sensorParams[SensorParameters.TYPE.value]
        sensor = database.sensorAccess.get_sensor_by_name_and_device_id(deviceID, sensorName)
        if sensor:
            return sensor

        database.sensorAccess.add_sensor(deviceID, sensorName, sensorType)
        return database.sensorAccess.get_sensor_by_name_and_device_id(deviceID, sensorName)

    return routes
