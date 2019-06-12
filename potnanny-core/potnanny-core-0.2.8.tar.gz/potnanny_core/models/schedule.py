import re
import json
import datetime
from sqlalchemy import (Column, Integer, String, DateTime, Boolean, Text,
        ForeignKey, func)
from sqlalchemy.orm import relationship
from potnanny_core.database import Base, db_session
from potnanny_core.schemas.outlet import GenericOutletSchema
from potnanny_core.models.weekday import WeekdayMap
from potnanny_core.models.outlet import OutletController
from potnanny_core.models.room import Room


class ScheduleOnOff(Base):
    """Store on/off schedule information."""

    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), nullable=False)
    outlet = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    days = Column(Integer, nullable=False, default=127)
    on_utc_hour = Column(Integer, nullable=False, default=0)
    on_minute = Column(Integer, nullable=False, default=0)
    off_utc_hour = Column(Integer, nullable=False, default=0)
    off_minute = Column(Integer, nullable=False, default=0)
    created = Column(DateTime, default=func.now())

    # relationships
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)


    def __repr__(self):
        return "<ScheduleOnOff({})>".format(self.name)


    def action_now(self, now=datetime.datetime.utcnow()):
        """
        Check if on/off schedules run now.

        args:
            none
        returns:
            None, or dict: dict will be outlet spec to pass to Action handler,
            like:
                {'outlet': {
                    'id': '2',
                    'name': 'foo',
                    'type': 'wireless',
                    'state': 1
                    }
                }
        """

        if not self.is_active:
            return None

        dow = now.strftime("%A")
        days = WeekdayMap.weekdays_from_value(self.days)
        if dow not in days:
            return None

        for key in ['on', 'off']:
            minute = getattr(self, "_".join((key, 'minute')))
            utc_hour = getattr(self, "_".join((key, 'utc_hour')))
            if now.minute == minute and now.hour == utc_hour:
                state = 0
                if key == 'on':
                    state = 1

                # create an action-proxy compliant dict object
                outlet = {'outlet': json.loads(self.outlet)}
                outlet['outlet']['state'] = state
                return outlet

        return None


class RoomLightManager(object):
    """
    Class to manage growth and flowering light schedules for rooms.

    While other ScheduleOnOff objects can be renamed, the objects managed
    by this class should never be renamed, as it will break the system.
    """

    def __init__(self, room_id):
        self.room_id = room_id
        self.room = Room.query.get(room_id)
        if not self.room:
            raise ValueError("Room with id %d not found" % room_id)

        self.schedule_names = ['lights growth schedule', 'lights flowering schedule']


    def schedules(self):
        """Query all schedules for this room."""
        return ScheduleOnOff.query.filter(
            ScheduleOnOff.room_id == self.room.id).filter(
            ScheduleOnOff.name.in_(self.schedule_names)).all()


    def active_schedule(self):
        """
        Query only the current active schedule for this room.

        args:
            none
        returns:
            a ScheduleOnOff object, or None if none are active
        """

        for s in self.schedules():
            if s.is_active:
                return s

        return None


    def expect_lights(self, now=datetime.datetime.utcnow()):
        """
        Do we expect lights to be on at this time?

        args:
            datetime: utcnow is default
        returns:
            bool.
        """

        sched = self.active_schedule()
        if not sched:
            return False

        dow = now.strftime("%A")
        days = WeekdayMap.weekdays_from_value(sched.days)
        if dow not in days:
            return False

        start = datetime.time(sched.on_utc_hour, sched.on_minute)
        end = datetime.time(sched.off_utc_hour, sched.off_minute)

        if now.time() > start and now.time() < end:
            return True

        return False


    def current_phase(self):
        """
        Get current room light phase schedule (growth|flowering|None)

        args:
            none
        returns:
            str: (growth|flowering)
        """
        for s in self.schedules():
            if s.is_active:
                match = re.search(r'(growth|flowering)', s.name, re.IGNORECASE)
                if match:
                    return match.group(1).lower()

        return None


    def switch_to_phase(self, phase):
        """
        Switch room light schedule to growth or flower phase.

        args:
            str: (growth|flowering)
        returns:
            none
        """
        if phase not in ['growth', 'flowering']:
            raise ValueError("Value must be 'growth' or 'flowering'")

        for s in self.schedules():
            if re.search(r'%s' % phase, s.name):
                s.is_active = True
            else:
                s.is_active = False

            s.synch_children()
            db_session.commit()


    def create_default_schedules(self, outlet):
        """
        Create default growth and flowering light schedules for a room.

        args:
            dict: outlet data
        returns:
            list of objects
        raises:
            none
        """
        for name in self.schedule_names:
            s = ScheduleOnOff.query.filter_by(name=name).first()
            if s:
                continue

            s = ScheduleOnOff(
                name=name,
                is_active=False,
                days=127,
                room_id=self.room_id,
                outlet=json.dumps(outlet),
            )
            db_session.add(s)
            db_session.commit()
            s.create_children()

            for c in s.children:
                if name == 'lights growth schedule':
                    # create an 18 hour lights-on schedule
                    if re.search(r'on', c.name, re.IGNORECASE):
                        c.on_utc_hour = 1
                        c.off_utc_hour = 19
                    else:
                        c.utc_hour = 19
                elif name == 'lights flowering schedule':
                    # create a 12 hour lights-on schedule
                    if re.search(r'on', c.name, re.IGNORECASE):
                        c.utc_hour = 4
                    else:
                        c.utc_hour = 16

                db_session.commit()

        # self.switch_to_schedule('growth')
        return self.schedules()
