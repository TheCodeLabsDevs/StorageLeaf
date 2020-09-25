from enum import Enum


class DeviceParameters(Enum):
    DEVICE = 'device'
    SENSORS = 'sensors'

    @staticmethod
    def get_values():
        return [m.value for m in DeviceParameters]


class SensorParameters(Enum):
    NAME = 'name'
    TYPE = 'type'
    VALUE = 'value'
    DEVICE_ID = 'device_id'

    @staticmethod
    def get_values():
        return [m.value for m in SensorParameters]


class MeasurementParameters(Enum):
    SENSOR_ID = 'sensor_id'
    VALUE = 'value'

    @staticmethod
    def get_values():
        return [m.value for m in MeasurementParameters]

