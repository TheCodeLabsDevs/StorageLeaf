from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from logic.databaseNew.Database import Base


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    sensors = relationship('Sensor', back_populates='device', cascade='all,delete')


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(String, index=True, nullable=False)
    deviceId = Column(Integer, ForeignKey('device.id'))

    device = relationship('Device', back_populates='sensors')
