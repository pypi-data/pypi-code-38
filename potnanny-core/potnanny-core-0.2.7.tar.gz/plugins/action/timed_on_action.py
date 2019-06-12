import json
import logging
import datetime
from potnanny_core.models.trigger import Trigger
from potnanny_core.models.outlet import OutletController
from potnanny_core.models.action import SingularAction
from potnanny_core.models.plugin import ActionPluginBase
from potnanny_core.database import db_session
from potnanny_core.utils import eval_condition

logger = logging.getLogger('potnanny.plugins.timed_on_action')


class TriggeredTimedOnAction(ActionPluginBase):
    """
    Class that will power an outlet on when a fault threshold is crossed, and
    turn the outlet back off N minutes later.
    """

    action_name = 'Outlet Timed-On'

    def __init__(self, *args, **kwargs):
        self.on_condition = None
        self.on_value = None
        self.on_minutes = 0
        self.outlet = None

        required = ['on_condition', 'on_value', 'on_minutes', 'outlet']
        for k, v in kwargs.items():
            if k in required:
                setattr(self, k, v)

        for r in required:
            if getattr(self, r) is None:
                raise ValueError("{} must provide value for '{}'".format(
                    self.__name__, r))


    def __repr__(self):
        return json.dumps(self.as_dict())


    def as_dict(self):
        return {
            'class': self.__class__.__name__,
            'name': self.__class__.action_name,
            'on_condition': self.on_condition,
            'on_value': self.on_value,
            'on_minutes': self.on_minutes,
            'outlet': self.outlet,
        }


    def interface(self):
        """Return JSON descriptor of input interface."""

        oc = OutletController()
        outlets = oc.available_outlets()
        conditions = [('lt', 'less than'), ('gt', 'greater than')]
        data = [
            {'outlet': {
                'type': 'select',
                'choices': outlets,
                'required': True,
                'label': 'Outlet',
                'id': 'plugin_outlet',
                }
            },
            {'on_condition': {
                'type': 'select',
                'choices': conditions,
                'required': True,
                'label': 'On Condition',
                'id': 'plugin_on_condition',
                },
            'on_value': {
                'type': 'int',
                'required': True,
                'label': 'On Value',
                'id': 'plugin_on_value'
                }
            },
            {'on_minutes': {
                'type': 'int',
                'required': True,
                'label': 'On Minutes',
                'id': 'plugin_on_minutes',
                },
            }
        ]

        return json.dumps(data)


    def html_interface(self):
        """
        Return html data used by web gui to present and validate input data.
        Each element must have an ID that is like "plugin_" + attribute_name

        The MVC Controller function that handles the form must strip the
        plugin_ prefix from the id names as required.

        args:
            - none
        returns:
            str: html data
        raises:
            none
        """

        oc = OutletController()
        outlets = oc.available_outlets()
        conditions = [('lt', 'less than'), ('gt', 'greater than')]
        template = Template("""
            <div class="row">
              Outlet <select id="plugin_outlet">
                {% for o in outlets %}
                  <option value={{ o | tojson }}>{{ o['name'] }}</option>
                {% endfor %}
              </select>
            </div>

            <div class="row">
              ON Condition <select id="plugin_on_condition">
              {% for c in conditions %}
                <option value="{{ c[0] }}">{{ c[1] }}</option>
              {% endfor %}
              </select>
              ON Value <input type="text" id="plugin_on_threshold">
              ON Minutes <input type="text" id="plugin_on_minutes">
            </div>
        """)

        return template.render(outlets=outlets, conditions=conditions)


    def handle_measurement(self, parent, meas):
        """
        eval a measurement value, see what actions, if any, it will trigger

        args:
            - the Action instance that is our parent
            - a Measurement instance
        returns:
            None
        """

        now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        trigger = None
        if parent.triggers:
            trigger = parent.triggers[0]


        def make_trigger():
            closed = now + datetime.timedelta(minutes=self.on_minutes)
            if parent.sleep_minutes:
                closed = closed + datetime.timedelta(minutes=parent.sleep_minutes)

            opts = {
                'action_id': parent.id,
                'created': now,
                'closed': closed,
            }

            t = Trigger(**opts)
            db_session.add(t)
            db_session.commit()


        if not trigger and eval_condition(meas.value, " ".join(('value', self.on_condition, self.on_value))):
            oc = OutletController()
            success = oc.turn_on(self.outlet)
            if success:
                make_trigger()

                # create an action that our ActionRouter handler will recognize
                # to switch the outlet off at a future time
                data = {'outlet': {'state': 0}}
                data['outlet'].update(self.outlet)

                future_time = now + datetime.timedelta(minutes=self.on_minutes)
                sa = SingularAction(
                    utc_runtime=future_time,
                    action=json.dumps(data),
                )
                db_session.add(sa)
                db_session.commit()

            return
