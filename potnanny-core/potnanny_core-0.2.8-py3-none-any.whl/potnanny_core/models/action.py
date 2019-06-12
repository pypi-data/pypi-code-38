import datetime
from sqlalchemy import (Column, Integer, String, Text, Boolean, Float,
        DateTime, ForeignKey, func)
from sqlalchemy.orm import relationship
from potnanny_core.database import Base
from potnanny_core.utils import rehydrate_plugin_instance
from potnanny_core.models.trigger import Trigger
from potnanny_core.models.outlet import OutletController
from potnanny_core.models.measurement import Measurement
from potnanny_core.models.plugin import ActionPluginBase


class Action(Base):
    """A class to define something that should happen based on a measurement.

    The 'plugin' attribute contains JSON text that will be used to rehydrate
    an instance of a plugin class.
    Example:
        "{
            'class': 'TriggeredOnOffAction',
            'on_condition': 'gt',
            'on_value': 80,
            'off_condition': 'lt',
            'off_value': 75,
            'outlet': {
                'name': 'test outlet',
                'id': '1',
                'type': 'wireless'
            }
        }"

    The 'sensor' field expects a STR, it can be set to 'any', as in 'any sensor that reports temperature', or
    a digit str that will refer to the id of a specific room sensor.
    """

    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), nullable=False)
    measurement_type = Column(String(24), nullable=False)
    sensor = Column(String(16), nullable=False, default="any")
    is_active = Column(Boolean, default=True)
    plugin = Column(Text, nullable=False)
    sleep_minutes = Column(Integer, nullable=False, default=0)
    created = Column(DateTime, default=func.now())

    # relationships
    room_id = Column(Integer, ForeignKey('rooms.id'))
    triggers = relationship('Trigger',
        primaryjoin="and_( Action.id==Trigger.action_id, or_(Trigger.closed == None, Trigger.closed > func.now()) )",
        backref='action',
        lazy=True,
        cascade='all,delete')


    def __repr__(self):
        return "<Action({})>".format(self.name)


    def eval_measurement(self, m):
        """
        Evaluate a measurement object, determine if it meets our requirements
        and should be passed on to the plugin child.

        args:
            - a Measurement object
        returns:
            none
        raises:
            none
        """
        if m.type != self.measurement_type:
            return

        if self.sensor == 'any' or int(self.sensor) == m.sensor_id:
            data = json.loads(self.plugin)
            cls = data.pop('class')

            plugin = rehydrate_plugin_instance(ActionPluginBase, cls, data)
            plugin.handle_measurement(self, m)

        return


class SingularAction(Base):
    """An action or event that is scheduled to take place only once.

    The 'action' attribute contains JSON text that will be handled by the
    appropriate handler.
    Example (turn an outlet on):
        "{'outlet': {
                'name': 'test outlet',
                'id': '1',
                'type': 'wireless',
                'state': 1,
            }
        }"
    """

    __tablename__ = 'singular_actions'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now())
    utc_runtime = Column(DateTime, nullable=False)
    completed = Column(DateTime, nullable=True)
    status = Column(String(48), nullable=True)
    action = Column(Text, nullable=False)

    def __repr__(self):
        return "<SingularAction({})>".format(self.id)

    def runs_now(self, now=datetime.datetime.utcnow()):
        """
        Check current time, evaluate if this action should run now.

        args:
            datetime: defaults to utcnow.
        returns:
            bool
        """

        now = now.replace(second=0, microsecond=0)
        then = self.utc_runtime.replace(second=0, microsecond=0)
        if now == then:
            return True

        return False


class ActionRouter(object):
    """Class to handle routing of proxy actions to the appropriate controllers."""

    @classmethod
    def route(cls, data):
        """
        Handle an action from Singular or Recurring actions.

        args:
            - dict. The top level key determines how we route the action.
                    For example:
                        {'outlet': {
                            'id': 1, 'type': 'wireless', 'state': 1
                        } }
                    The 'outlet' key indicates this action should be routed
                    to an instance of OutletController.
        returns:
            bool
        raises:
            RuntimeError if action is unrecognized
        """

        if 'outlet' in data.keys():
            oc = OutletController()
            return oc.switch_outlet(data['outlet'])

        # TODO: add more routers. But, no other types are yet identified.
        raise RuntimeError("Unknown action routing type")
