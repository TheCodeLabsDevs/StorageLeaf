from flask import Blueprint, jsonify

from logic.AuthenticationWrapper import require_api_key
from logic.database.Database import Database


def construct_blueprint(settings):
    devices = Blueprint('devices', __name__)

    @devices.route('/devices', methods=['GET'])
    def get_all_devices():
        database = Database(settings['database']['databasePath'])
        return jsonify(database.deviceAccess.get_all_devices())

    @devices.route('/device/<int:deviceID>', methods=['GET'])
    def get_device(deviceID):
        database = Database(settings['database']['databasePath'])
        return jsonify(database.deviceAccess.get_device(deviceID))

    @devices.route('/device/<int:deviceID>/sensors/', methods=['GET'])
    def get_all_sensors_for_device(deviceID):
        database = Database(settings['database']['databasePath'])
        device = database.deviceAccess.get_device(deviceID)
        if not device:
            return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

        return jsonify(database.sensorAccess.get_all_sensors_for_device(deviceID))

    @devices.route('/device/<int:deviceID>', methods=['DELETE'])
    @require_api_key(password=settings['api']['key'])
    def delete_device(deviceID):
        database = Database(settings['database']['databasePath'])
        if not database.deviceAccess.get_device(deviceID):
            return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

        sensors = database.sensorAccess.get_all_sensors_for_device(deviceID)
        for sensor in sensors:
            database.measurementAccess.delete_measurements_for_sensor(sensor['id'])
            database.sensorAccess.delete_sensor(sensor['id'])

        database.deviceAccess.delete_device(deviceID)

        return jsonify({'success': True})

    return devices
