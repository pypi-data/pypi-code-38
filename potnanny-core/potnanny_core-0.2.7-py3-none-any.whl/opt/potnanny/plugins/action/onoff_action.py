import json
import logging
import datetime
from jinja2 import Template
from potnanny_core.models.trigger import Trigger
from potnanny_core.models.outlet import OutletController
from potnanny_core.models.plugin import ActionPluginBase
from potnanny_core.database import db_session
from potnanny_core.utils import eval_condition
# from potnanny_core.models.outlet import OutletController

logger = logging.getLogger('potnanny.plugins.onoff_action')


class TriggeredOnOffAction(ActionPluginBase):
    """Power an outlet ON or OFF when thresholds are crossed."""

    action_name = 'Outlet On/Off'

    def __init__(self, *args, **kwargs):
        """
        initialize plugin instance

        keyword-args:
            on_condition: str (like, 'gt','lt','le','ge','eq' etc...)
            on_value: int (the value threshold a measurement must cross)
            off_condition: str (see on_condition)
            off_value: int
            outlet: str (json txt like '{"id": "1", "type": "wireless"}')
        """
        self.on_condition = None
        self.on_threshold = None
        self.off_condition = None
        self.off_threshold = None
        self.outlet = None

        required = ['on_condition', 'off_condition', 'on_value', 'off_value',
            'outlet']

        for k, v in kwargs.items():
            if k in required:
                setattr(self, k, v)

        for r in required:
            if getattr(self, r) is None:
                raise ValueError("{} must provide value for '{}'".format(
                    self.__class__.__name__, r))


    def __repr__(self):
        return json.dumps(self.as_dict())


    def as_dict(self):
        """Returns basic dict representation."""

        return {
            'class': self.__class__.__name__,
            'on_condition': self.on_condition,
            'on_value': self.on_value,
            'off_condition': self.off_condition,
            'off_value': self.off_value,
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
                }
            },
            {'on_value': {
                'type': 'int',
                'required': True,
                'label': 'On Value',
                'id': 'plugin_on_value'
                }
            },
            {'off_condition': {
                'type': 'select',
                'choices': conditions,
                'required': True,
                'label': 'Off Condition',
                'id': 'plugin_off_condition',
                }
            },
            {'off_value': {
                'type': 'int',
                'required': True,
                'label': 'Off Value',
                'id': 'plugin_off_value',
                }
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
            </div>

            <div class="row">
              OFF Condition <select id="plugin_off_condition">
                {% for c in conditions %}
                  <option value="{{ c[0] }}">{{ c[1] }}</option>
                {% endfor %}
              </select>
              OFF Value <input type="text" id="plugin_off_threshold">
            </div>
        """)

        return template.render(outlets=outlets, conditions=conditions)


    def handle_measurement(self, parent, meas):
        """
        Eval a measurement value, see what actions, if any, it will trigger

        args:
            - the Action instance that is our parent
            - a Measurement instance
        returns:
            a dict of action details, or None
        """

        logger.debug("handling measurement {}, {}".format(parent, meas))
        now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        trigger = None
        if parent.triggers:
            trigger = parent.triggers[0]


        def make_trigger():
            opts = {
                'action_id': parent.id,
                'created': now,
            }
            if parent.sleep_minutes:
                opts['closed'] = now + datetime.timedelta(minutes=parent.sleep_minutes)

            t = Trigger(**opts)
            db_session.add(t)
            db_session.commit()


        if eval_condition(meas.value, " ".join(('value', self.on_condition, self.on_value))):
            logger.debug("turning outlet '{}' ON".format(self.outlet))
            oc = OutletController()
            result = oc.turn_on(self.outlet)
            # create a trigger only if action was successful
            if result:
                if trigger is None:
                    make_trigger()

            return

        if eval_condition(meas.value, " ".join(('value', self.off_condition, self.off_value))):
            logger.debug("turning outlet '{}' OFF".format(self.outlet))
            oc = OutletController()
            result = oc.turn_off(self.outlet)
            if result and trigger and trigger.closed == None:
                trigger.closed = now
                db_session.commit()

            return
