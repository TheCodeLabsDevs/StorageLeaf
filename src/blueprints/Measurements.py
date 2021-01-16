from typing import Dict

from flask import Blueprint, jsonify, request

from logic.AuthenticationWrapper import require_api_key
from logic.BackupService import BackupService
from logic.Parameters import DeviceParameters, SensorParameters, MeasurementParameters
from logic.RequestValidator import RequestValidator, ValidationError
from logic.database.Database import Database


def construct_blueprint(settings: Dict, backupService: BackupService):
    measurements = Blueprint('measurements', __name__)

    @measurements.route('/measurements/minMax', methods=['GET'])
    def get_min_and_max_for_sensor_ids():
        if 'sensorIds' not in request.args:
            return jsonify({'message': 'Parameter "sensorIds" missing'}), 400

        if 'startDateTime' not in request.args:
            return jsonify({'message': 'Parameter "startDateTime" missing'}), 400

        if 'endDateTime' not in request.args:
            return jsonify({'message': 'Parameter "endDateTime" missing'}), 400

        sensorIds = request.args.get('sensorIds').split(',')
        startDateTime = request.args.get('startDateTime')
        endDateTime = request.args.get('endDateTime')

        database = Database(settings['database']['databasePath'], backupService)

        values = []
        for sensorId in sensorIds:
            sensorId = int(sensorId)
            measurementsForSensor = database.measurementAccess.get_all_measurements_for_sensor(sensorId,
                                                                                               startDateTime,
                                                                                               endDateTime)
            for measurement in measurementsForSensor:
                values.append(float(measurement['value']))

        if values:
            return jsonify({
                'min': min(values),
                'max': max(values)
            })

        return jsonify({
            'min': None,
            'max': None
        })

    @measurements.route('/measurements', methods=['POST'])
    @require_api_key(password=settings['api']['key'])
    def add_multiple_measurements():
        try:
            parameters = RequestValidator.validate(request, DeviceParameters.get_values())
            database = Database(settings['database']['databasePath'], backupService)

            deviceName = parameters[DeviceParameters.DEVICE.value]
            if not database.deviceAccess.get_device_by_name(deviceName):
                database.deviceAccess.add_device(deviceName)
            device = database.deviceAccess.get_device_by_name(deviceName)

            sensors = parameters[DeviceParameters.SENSORS.value]
            for sensor in sensors:
                sensorParams = RequestValidator.validate_parameters(sensor,
                                                                    [SensorParameters.NAME.value,
                                                                     SensorParameters.TYPE.value,
                                                                     SensorParameters.VALUE.value],
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

    @measurements.route('/measurement', methods=['POST'])
    @require_api_key(password=settings['api']['key'])
    def add_single_measurement():
        try:
            parameters = RequestValidator.validate(request, MeasurementParameters.get_values())
            database = Database(settings['database']['databasePath'], backupService)

            sensorID = parameters[MeasurementParameters.SENSOR_ID.value]
            if not database.sensorAccess.get_sensor(sensorID):
                return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

            database.measurementAccess.add_measurement(sensorID, parameters[SensorParameters.VALUE.value])
        except ValidationError as e:
            return e.response, 400

        return jsonify({'success': True})

    return measurements
