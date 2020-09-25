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

    @staticmethod
    def get_values():
        return [m.value for m in SensorParameters]
