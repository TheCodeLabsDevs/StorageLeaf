from typing import Dict

from flask import Blueprint, jsonify, request

from logic.BackupService import BackupService
from logic.database.Database import Database


def construct_blueprint(settings: Dict, backupService: BackupService):
    sensors = Blueprint('sensors', __name__)

    @sensors.route('/sensor/<int:sensorID>/measurements', methods=['GET'])
    def get_all_measurements_for_sensor_with_limit(sensorID: int):
        database = Database(settings['database']['databasePath'], backupService)
        sensor = database.sensorAccess.get_sensor(sensorID)
        if not sensor:
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        startDateTime = request.args.get('startDateTime')
        endDateTime = request.args.get('endDateTime')

        database = Database(settings['database']['databasePath'], backupService)
        return jsonify(database.measurementAccess.get_all_measurements_for_sensor(sensorID, startDateTime, endDateTime))

    @sensors.route('/sensor/<int:sensorID>/measurements/latest', methods=['GET'])
    def get_latest_measurements_for_sensor(sensorID: int):
        database = Database(settings['database']['databasePath'], backupService)
        sensor = database.sensorAccess.get_sensor(sensorID)
        if not sensor:
            return jsonify({'success': False, 'msg': f'No sensor with id "{sensorID}" existing'})

        return jsonify(database.measurementAccess.get_latest_measurements_for_sensor(sensorID))

    return sensors
