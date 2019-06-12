from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, func)
from sqlalchemy.orm import relationship

from potnanny_core.database import Base
from potnanny_core.utils import convert_celsius
from potnanny_core.models.measurement import Measurement
from potnanny_core.models.setting import TemperatureDisplay

class Sensor(Base):
    """Store bluetooth sensor information."""

    __tablename__ = 'sensors'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), default='my sensor')
    address = Column(String(48), unique=True, nullable=False)
    model = Column(String(48), nullable=True)
    created = Column(DateTime, default=func.now())

    # relationships
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)

    def __repr__(self):
        return "<Sensor({})>".format(self.name)


    def latest_readings(self):
        """
        Get all the latest measurement values from this sensor

        args:

        returns:
            a dict
        """

        temp_disp = TemperatureDisplay.get()
        data = {}
        results = db_session.query(
            Measurement.type, Measurement.value, func.max(Measurement.created)
            ).filter(Measurement.sensor_id == self.id).order_by(
            Measurement.created.desc(), Measurement.type).group_by(
            Measurement.type).all()

        if not results:
            return {}

        for r in results:
            # all db temp measurements are in celsius. always
            if temp_disp == 'fahrenheit' and r[0] == 'temperature':
                data[r[0]] = convert_celsius(r[1])
            else:
                data[r[0]] = r[1]

        return data


    def measurement_types(self):
        """
        get list of all valid measurement types for this sensor, based what it
        has reported in the past.

        args:

        returns:
            a list ['battery', 'temperature', 'humidity']
        """
        results = db_session.query(Measurement.type).filter(
            Measurement.sensor_id == self.id).order_by(
            Measurement.type).group_by(
            Measurement.type).all()

        if not results:
            return []

        return [r[0] for r in results]
