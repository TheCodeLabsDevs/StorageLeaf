from typing import Dict

from flask import Blueprint, jsonify, request

from logic.AuthenticationWrapper import require_api_key
from logic.database.Database import Database
from logic.Parameters import DeviceParameters, SensorParameters
from logic.RequestValidator import RequestValidator, ValidationError


def construct_blueprint(settings):
    measurements = Blueprint('measurements', __name__)

    @measurements.route('/measurements', methods=['GET'])
    def get_all_measurements():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.measurementAccess.get_all_measurements())

    @measurements.route('/measurement/<int:measurementID>', methods=['GET'])
    def get_measurement(measurementID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.measurementAccess.get_measurement(measurementID))

    @measurements.route('/measurements', methods=['POST'])
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

    @measurements.route('/measurement/<int:measurementID>', methods=['DELETE'])
    @require_api_key(password=settings['api']['key'])
    def delete_measurement(measurementID):
        database = Database(settings['database']['databasePath'])
        if not database.measurementAccess.get_measurement(measurementID):
            return jsonify({'success': False, 'msg': f'No measurement with id "{measurementID}" existing'})

        database.measurementAccess.delete_measurement(measurementID)
        return jsonify({'success': True})

    return measurements
