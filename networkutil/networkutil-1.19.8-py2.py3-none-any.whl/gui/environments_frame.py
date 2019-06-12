# encoding: utf-8

import logging_helper
from uiutil.tk_names import askquestion, showerror
from uiutil.frame.dynamic import add_layout_config, LAYOUT_CFG, DynamicFrame
from ..resources import templates
from ..endpoint_config import ENVIRONMENTS_CONFIG, EnvAndAPIs, Endpoints

logging = logging_helper.setup_logging()

ROOT_LAYOUT = u'{c}.root_layouts.env_config_layout'.format(c=LAYOUT_CFG)
ADD_LAYOUT = u'{c}.root_layouts.add_env_layout'.format(c=LAYOUT_CFG)


class EnvironmentsFrame(DynamicFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        # Set the config initialisation parameters
        add_layout_config(templates.environments_layout)

        self.endpoints = Endpoints()
        self.env_and_apis = EnvAndAPIs()

        super(EnvironmentsFrame, self).__init__(*args, **kwargs)

    # Button Helpers
    def add_env_name_trace(self,
                           widget_name,
                           widget_var):

        logging.debug(u'WIDGET_NAME: {n}'.format(n=widget_name))
        logging.debug(u'WIDGET_VAR: {v}'.format(v=widget_var.get()))

        # Split the device name off the widget name
        item_name = widget_var.get()
        logging.debug(u'NAME: {v}'.format(v=item_name))

        self.item_dict_name = item_name

    # Button Methods
    def add(self):
        self.update_layout(ADD_LAYOUT)

    def delete(self):
        selected = self.selected.get()
        logging.debug(u'SELECTED: {d}'.format(d=selected))

        if len(self.cfg[ENVIRONMENTS_CONFIG]) <= 1:
            showerror(u'Delete Environment',
                      u'Cannot remove last environment!',
                      parent=self)

        elif self.endpoints.environment_is_used(selected):
            showerror(u'Delete Environment',
                      u'Cannot remove, environment used in endpoint config!',
                      parent=self)

        elif self.env_and_apis.environment_is_used_by_api:
            showerror(u'Delete Environment',
                      u'Cannot remove, environment used in API config!',
                      parent=self)

        else:
            result = askquestion(u"Delete Environment",
                                 u"Are you sure you want to delete: {item}?".format(item=selected),
                                 parent=self)

            if result == u'yes':
                config = self.cfg[ENVIRONMENTS_CONFIG]
                idx = config.index(selected)
                del config[idx]
                self.cfg[ENVIRONMENTS_CONFIG] = config

                # Update selected
                self.selected.set(self.cfg[ENVIRONMENTS_CONFIG][0])

                self.refresh()

    def cancel(self):
        self.return_to_root_layout()

    def save(self):
        config = self.cfg[ENVIRONMENTS_CONFIG]
        config.append(self.item_dict_name)
        self.cfg[ENVIRONMENTS_CONFIG] = config

        self.return_to_root_layout()
