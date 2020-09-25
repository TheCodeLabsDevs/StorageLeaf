from enum import Enum

from flask import Blueprint, jsonify

from logic.Database import Database


class DeviceParameters(Enum):
    DEVICE = 'device'
    SENSORS = 'sensors'

    @staticmethod
    def get_values():
        return [m.value for m in DeviceParameters]


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

    return devices
