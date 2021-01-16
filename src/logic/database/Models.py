from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from logic.database.Database import Base


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)

    sensors = relationship('Sensor', back_populates='device', cascade='all,delete')


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    type = Column(String, index=True, nullable=False)
    deviceId = Column(Integer, ForeignKey('device.id'))

    device = relationship('Device', back_populates='sensors')
    measurements = relationship('Measurement', back_populates='sensor', cascade='all,delete')


class Measurement(Base):
    __tablename__ = 'measurement'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(String, index=True, nullable=False)
    value = Column(String, index=True, nullable=False)
    sensorId = Column(Integer, ForeignKey('sensor.id'))

    sensor = relationship('Sensor', back_populates='measurements')
