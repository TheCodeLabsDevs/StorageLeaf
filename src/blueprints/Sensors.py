from flask import Blueprint, jsonify, request

from logic.AuthenticationWrapper import require_api_key
from logic.Parameters import SensorParameters
from logic.RequestValidator import RequestValidator, ValidationError
from logic.database.Database import Database


def construct_blueprint(settings):
    sensors = Blueprint('sensors', __name__)

    @sensors.route('/sensors', methods=['GET'])
    def get_all_sensors():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.sensorAccess.get_all_sensors())

    @sensors.route('/sensor/<int:sensorID>', methods=['GET'])
    def get_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.sensorAccess.get_sensor(sensorID))

    @sensors.route('/sensor/<int:sensorID>/measurements', methods=['GET'])
    def get_all_measurements_for_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        sensor = database.sensorAccess.get_sensor(sensorID)
        if not sensor:
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        return jsonify(database.measurementAccess.get_all_measurements_for_sensor(sensorID))

    @sensors.route('/sensor/<int:sensorID>/measurements/latest', methods=['GET'])
    def get_latest_measurements_for_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        sensor = database.sensorAccess.get_sensor(sensorID)
        if not sensor:
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        return jsonify(database.measurementAccess.get_latest_measurements_for_sensor(sensorID))

    @sensors.route('/sensor/<int:sensorID>', methods=['DELETE'])
    @require_api_key(password=settings['api']['key'])
    def delete_sensor(sensorID):
        database = Database(settings['database']['databasePath'])
        if not database.sensorAccess.get_sensor(sensorID):
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        database.measurementAccess.delete_measurements_for_sensor(sensorID)
        database.sensorAccess.delete_sensor(sensorID)
        return jsonify({'success': True})

    @sensors.route('/sensor', methods=['POST'])
    @require_api_key(password=settings['api']['key'])
    def add_sensor():
        try:
            parameters = RequestValidator.validate(request, [SensorParameters.NAME.value,
                                                             SensorParameters.TYPE.value,
                                                             SensorParameters.DEVICE_ID.value])
            database = Database(settings['database']['databasePath'])

            deviceID = parameters[SensorParameters.DEVICE_ID.value]
            sensorName = parameters[SensorParameters.NAME.value]
            sensorType = parameters[SensorParameters.TYPE.value]

            device = database.deviceAccess.get_device(deviceID)
            if not device:
                return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

            existingSensor = database.sensorAccess.get_sensor_by_name_and_device_id(deviceID, sensorName)
            if existingSensor:
                return jsonify({'success': False,
                                'msg': f'A sensor called "{sensorName}" already exists (ID: {existingSensor["id"]}) for device {deviceID}'})

            database.sensorAccess.add_sensor(deviceID, sensorName, sensorType)
        except ValidationError as e:
            return e.response, 400

        return jsonify({'success': True})

    return sensors
