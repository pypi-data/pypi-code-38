# encoding: utf-8

import logging_helper
from uiutil.tk_names import askquestion, showerror
from uiutil.frame.dynamic import add_layout_config, LAYOUT_CFG, DynamicFrame
from ..resources import templates
from ..endpoint_config import ENDPOINTS_CONFIG, Endpoints, EnvAndAPIs, EPConstant

logging = logging_helper.setup_logging()

ROOT_LAYOUT = u'{c}.root_layouts.endpoint_config_layout'.format(c=LAYOUT_CFG)
ADD_LAYOUT = u'{c}.root_layouts.add_endpoint_layout'.format(c=LAYOUT_CFG)
EDIT_LAYOUT = u'{c}.root_layouts.edit_endpoint_layout'.format(c=LAYOUT_CFG)

DEFAULT_ENDPOINT = {
    u'port': 80,
    u'environment': u'',
    u'apis': []
}


class EndpointsFrame(DynamicFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        # Set the config initialisation parameters
        add_layout_config(templates.endpoint_layout)

        self.endpoints = Endpoints()
        self.env_and_apis = EnvAndAPIs()

        super(EndpointsFrame, self).__init__(*args, **kwargs)

    @property
    def environments(self):
        return self.env_and_apis.get_environments()

    # Button Helpers
    def update_item(self,
                    var_name,
                    var):

        logging.debug(u'VAR_NAME: {n}'.format(n=var_name))
        logging.debug(u'VAR: {v}'.format(v=var.get()))

        widget_name_parts = var_name.split(u'_')

        # Split the device name off the widget name
        item_name = u'_'.join(widget_name_parts[4:-1])
        logging.debug(u'ITEM_NAME: {v}'.format(v=item_name))

        key = u'{c}.{i}.{v}'.format(c=ENDPOINTS_CONFIG,
                                    i=item_name,
                                    v=widget_name_parts[2])
        logging.debug(u'KEY: {v}'.format(v=key))

        self.cfg[key] = var.get()

    def update_env(self,
                   event):

        frame = self.frames[u'endpoint_add_edit_item_frame']
        env = getattr(frame, u'{n}_var'.format(n=event.widget.name)).get()

        self.item_dict[EPConstant.env] = env
        self._update_api_checkbox_states(env)

    def _update_api_checkbox_states(self,
                                    env):

        frame = self.frames[u'endpoint_add_edit_api_frame']
        configured_apis = self.env_and_apis.get_apis_for_environment(env)

        for api in self.env_and_apis.get_api_list():
            checkbox = getattr(frame, u'_api_checkbox_{a}'.format(a=api))
            checkbox.config(state=u'normal' if api in configured_apis else u'disabled')

    def update_apis(self,
                    event):

        frame = self.frames[u'endpoint_add_edit_item_frame']
        apis = getattr(frame, u'{n}_var'.format(n=event.widget.name)).get()

        self.item_dict[EPConstant.apis] = apis

    def update_api_list(self):

        frame = self.frames[u'endpoint_add_edit_item_frame']
        api_combo = getattr(frame, u'_apis_combobox')
        env = getattr(frame, u'_env_combobox_var').get()
        logging.debug(u'ENV: {e}'.format(e=env))

        apis = self.env_and_apis.get_apis_for_environment(env)
        logging.debug(u'APIS: {a}'.format(a=apis))

        api_combo.config(values=apis)

    def add_endpoint_trace(self,
                           var_name,
                           var):

        logging.debug(u'VAR_NAME: {n}'.format(n=var_name))
        logging.debug(u'VAR: {v}'.format(v=var.get()))

        # Split the device name off the widget name
        item_name = var.get()
        logging.debug(u'NAME: {v}'.format(v=item_name))

        self.item_dict_name = item_name

    def add_edit_trace(self,
                       var_name,
                       var):

        logging.debug(u'VAR_NAME: {n}'.format(n=var_name))
        logging.debug(u'VAR: {v}'.format(v=var.get()))

        widget_name_parts = var_name.split(u'_')

        # Split the device name off the widget name
        item_name = widget_name_parts[1]
        logging.debug(u'ITEM_NAME: {v}'.format(v=item_name))

        item_value = var.get()
        logging.debug(u'ITEM_VALUE: {v}'.format(v=item_value))

        self.item_dict[item_name] = item_value

    def api_select_trace(self,
                         var_name,
                         var):

        logging.debug(u'VAR_NAME: {n}'.format(n=var_name))
        logging.debug(u'VAR: {v}'.format(v=var.get()))

        widget_name_parts = var_name.split(u'_')

        # Split the device name off the widget name
        item_name = u'_'.join(widget_name_parts[3:-1])
        logging.debug(u'ITEM_NAME: {v}'.format(v=item_name))

        item_value = var.get()
        logging.debug(u'ITEM_VALUE: {v}'.format(v=item_value))

        current_apis = self.item_dict.get(EPConstant.apis, [])

        try:
            cur_idx = current_apis.index(item_name)
            in_list = True

        except ValueError:
            cur_idx = -1
            in_list = False

        if var.get() and not in_list:
            current_apis.append(item_name)

        if not var.get() and in_list:
            del current_apis[cur_idx]

        self.item_dict[EPConstant.apis] = current_apis

    def _add_edit(self,
                  edit=False):

        self.item_list = self.env_and_apis.get_api_list()

        if edit:
            # Load item to be edited
            selected = self.selected.get()
            logging.debug(u'SELECTED: {d}'.format(d=selected))

            item_key = u'{c}.{i}'.format(c=ENDPOINTS_CONFIG,
                                         i=selected)

            self.item_dict_name = selected
            self.item_dict = self.cfg[item_key].copy()

            # Update the layout
            self.update_layout(EDIT_LAYOUT)

            # Update the checkboxes with their correct states and existing values
            env = self.item_dict.get(EPConstant.env)

            if env != u'':
                self._update_api_checkbox_states(env)

            frame = self.frames[u'endpoint_add_edit_api_frame']
            current_apis = self.item_dict.get(EPConstant.apis, [])

            for api in current_apis:
                checkbox = getattr(frame, u'_api_checkbox_{a}'.format(a=api))
                checkbox.invoke()

        else:
            # Load a blank item
            self.item_dict = DEFAULT_ENDPOINT

            self.update_layout(ADD_LAYOUT)

    # Button Methods
    def add(self):
        self._add_edit()

    def edit(self):
        self._add_edit(edit=True)

    def delete(self):
        selected = self.selected.get()
        logging.debug(u'SELECTED: {d}'.format(d=selected))

        if len(self.cfg[ENDPOINTS_CONFIG]) <= 1:
            showerror(u'Delete Endpoint',
                      u'Cannot remove last endpoint!',
                      parent=self)

        else:
            result = askquestion(u"Delete Endpoint",
                                 u"Are you sure you want to delete: {item}?".format(item=selected),
                                 parent=self)

            if result == u'yes':
                key = u'{c}.{i}'.format(c=ENDPOINTS_CONFIG,
                                        i=selected)

                del self.cfg[key]

                new_selected = self.cfg[ENDPOINTS_CONFIG].keys()[0]
                select_key = u'{c}.{k}'.format(c=ENDPOINTS_CONFIG,
                                               k=new_selected)

                default = self.default.get()

                if default == selected:
                    self.cfg[u'{c}.default'.format(c=select_key)] = True
                    self.default.set(new_selected)

                self.selected.set(new_selected)

                self.refresh()

    def cancel(self):
        self.return_to_root_layout()

    def save(self):

        key = u'{c}.{i}'.format(c=ENDPOINTS_CONFIG,
                                i=self.item_dict_name)

        self.cfg[key] = self.item_dict

        self.return_to_root_layout()
