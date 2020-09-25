from flask import Blueprint, jsonify

from logic.AuthenticationWrapper import require_api_key
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

    return sensors
