from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from potnanny_core.database import Base
from potnanny_core.utils import convert_celsius
from potnanny_core.models.sensor import Sensor
from potnanny_core.models.measurement import Measurement
from potnanny_core.models.action import Action
from potnanny_core.models.grow import Grow
from potnanny_core.models.setting import TemperatureDisplay

class Room(Base):
    """Room Class."""

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), unique=True, default='my room')
    notes = Column(Text)
    created = Column(DateTime, default=func.now())

    # relationships #
    sensors = relationship('Sensor', backref='room', lazy=True, cascade='all')
    actions = relationship('Action', backref='room',
                                cascade='all,delete', lazy=True)
    schedules = relationship('ScheduleOnOff', backref='room', lazy=True,
                                cascade='all,delete')

    # only active (not ended) grows are linked to the room.
    grows = relationship('Grow',
                primaryjoin="and_(Room.id==Grow.room_id, Grow.ended == None)",
                backref='room',
                cascade='all,delete',
                lazy=True)


    def __repr__(self):
        return "<Room({})>".format(self.name)


    def environment(self):
        """
        Most recent room environment values. If there are multiple sensors in a
        room producing the same type of measurements ('temperature' for example),
        one of them is picked randomly. No averaging is done.

        args:
            none
        returns:
            dict: like {'temperature': 20.0, 'humidity': 51.2}
        """

        data = {}
        temp_disp = TemperatureDisplay.get()
        if self.sensors:
            id_list = [s.id for s in self.sensors]
            results = Measurement.query.with_entities(
                    Measurement.type,
                    Measurement.value,
                    func.max(Measurement.created)).filter(
                    Measurement.sensor_id.in_(id_list)).filter(
                    Measurement.type != 'battery').group_by(
                    Measurement.type).all()

            for row in results:
                # all db temp measurements are in celsius. always
                if temp_disp == 'fahrenheit' and row[0] == 'temperature':
                    data[row[0]] = convert_celsius(row[1])
                else:
                    data[row[0]] = row[1]

        return data
