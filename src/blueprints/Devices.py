from typing import Dict

from flask import Blueprint, jsonify, request

from logic.AuthenticationWrapper import require_api_key
from logic.BackupService import BackupService
from logic.Parameters import DeviceParameters
from logic.RequestValidator import RequestValidator, ValidationError
from logic.database.Database import Database


def construct_blueprint(settings: Dict, backupService: BackupService):
    devices = Blueprint('devices', __name__)

    @devices.route('/devices', methods=['GET'])
    def get_all_devices():
        database = Database(settings['database']['databasePath'], backupService)
        return jsonify(database.deviceAccess.get_all_devices())

    @devices.route('/device/<int:deviceID>', methods=['GET'])
    def get_device(deviceID):
        database = Database(settings['database']['databasePath'], backupService)
        return jsonify(database.deviceAccess.get_device(deviceID))

    @devices.route('/device/<int:deviceID>/sensors/', methods=['GET'])
    def get_all_sensors_for_device(deviceID):
        database = Database(settings['database']['databasePath'], backupService)
        device = database.deviceAccess.get_device(deviceID)
        if not device:
            return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

        return jsonify(database.sensorAccess.get_all_sensors_for_device(deviceID))

    @devices.route('/device/<int:deviceID>', methods=['DELETE'])
    @require_api_key(password=settings['api']['key'])
    def delete_device(deviceID):
        database = Database(settings['database']['databasePath'], backupService)
        if not database.deviceAccess.get_device(deviceID):
            return jsonify({'success': False, 'msg': f'No device with id "{deviceID}" existing'})

        sensors = database.sensorAccess.get_all_sensors_for_device(deviceID)
        for sensor in sensors:
            database.measurementAccess.delete_measurements_for_sensor(sensor['id'])
            database.sensorAccess.delete_sensor(sensor['id'])

        database.deviceAccess.delete_device(deviceID)

        return jsonify({'success': True})

    @devices.route('/device', methods=['POST'])
    @require_api_key(password=settings['api']['key'])
    def add_device():
        try:
            parameters = RequestValidator.validate(request, [DeviceParameters.DEVICE.value])
            database = Database(settings['database']['databasePath'], backupService)

            deviceName = parameters[DeviceParameters.DEVICE.value]
            existingDevice = database.deviceAccess.get_device_by_name(deviceName)
            if existingDevice:
                return jsonify({'success': False,
                                'msg': f'A device called "{deviceName}" already exists (ID: {existingDevice["id"]})'})

            database.deviceAccess.add_device(deviceName)
        except ValidationError as e:
            return e.response, 400

        return jsonify({'success': True})

    return devices
