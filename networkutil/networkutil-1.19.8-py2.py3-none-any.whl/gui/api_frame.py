# encoding: utf-8

import ast
import logging_helper
from uiutil.tk_names import askquestion, showerror
from uiutil.frame.dynamic import add_layout_config, LAYOUT_CFG, DynamicFrame
from ..resources import templates
from ..endpoint_config import APIS_CONFIG, EnvAndAPIs, Endpoints, APIConstant

logging = logging_helper.setup_logging()

ROOT_LAYOUT = u'{c}.root_layouts.api_config_layout'.format(c=LAYOUT_CFG)
ADD_LAYOUT = u'{c}.root_layouts.add_api_layout'.format(c=LAYOUT_CFG)
ADD_EDIT_ENV_LAYOUT = u'{c}.root_layouts.add_edit_api_env_layout'.format(c=LAYOUT_CFG)


class APIFrame(DynamicFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        # Set the config initialisation parameters
        add_layout_config(templates.api_layout)

        self.endpoints = Endpoints()
        self.env_and_apis = EnvAndAPIs()

        super(APIFrame, self).__init__(*args, **kwargs)

        # Setup Add API entry validation attributes
        self.validate_add_api_entry = (self.register(self._validate_add_api_entry), u'%P')
        self.add_api_entry_valid = True
        self.validate_methods_entry = (self.register(self._validate_methods_entry), u'%P')
        self.methods_entry_valid = True
        self.validate_parameters_entry = (self.register(self._validate_parameters_entry), u'%P')
        self.parameters_entry_valid = True

    @property
    def apis(self):
        return self.env_and_apis.get_api_list()

    @property
    def environments(self):
        return self.env_and_apis.get_environments()

    @property
    def api_environments(self):
        return self.env_and_apis.get_environments_for_api(self.item_dict_name)

    def before_draw(self):
        selected = self.selected.get()

        # Setup initially selected api if nothing already selected
        apis = self.apis
        apis.sort()
        api_name = apis[0]
        api_key = u'{k}.{a}'.format(k=APIS_CONFIG,
                                    a=api_name)

        if selected is u'':
            self.selected.set(api_name)

        if len(self.item_dict.keys()) == 0:
            self.item_dict = self.cfg[api_key]

        if hasattr(self, u'combo_selected'):
            if self.combo_selected.get() == u'':
                self.combo_selected.set(self.selected.get())

        if hasattr(self, u'selected_env'):
            if self.selected_env.get() == u'':
                api_env = self.item_dict.keys()
                api_env.sort()
                self.selected_env.set(api_env[0])

    # Helper methods
    def update_api_env(self,
                       _):

        api_key = u'{k}.{a}'.format(k=APIS_CONFIG,
                                    a=self.combo_selected.get())

        self.selected.set(self.combo_selected.get())
        self.item_dict = self.cfg[api_key]

        logging.debug(u'ITEM DICT: {i}'.format(i=self.item_dict))

        self.refresh()

    def update_env_edit(self,
                        _):

        apis = self.cfg[APIS_CONFIG]
        api = apis.get(self.item_dict_name, {})

        self.selected.set(self.combo_selected.get())
        self.item_dict = api.get(self.combo_selected.get(), {})

        logging.debug(u'ITEM DICT: {i}'.format(i=self.item_dict))

        self.refresh()

    def _validate_add_api_entry(self,
                                value):

        logging.debug(u'Validating add API entry')

        entry = getattr(self.frames[u'add_api_frame'], u'_api_name_entry')
        existing = self.cfg[u'{k}'.format(k=APIS_CONFIG)].keys()

        self.add_api_entry_valid = False if value in existing or value == u'' else True

        entry.config(foreground=u'black' if self.add_api_entry_valid else u'red')

        return self.add_api_entry_valid

    def _validate_methods_entry(self,
                                value):

        logging.debug(u'Validating methods entry')

        entry = getattr(self.frames[u'add_edit_api_env_entry_frame'], u'_methods_entry')

        if value == u'':
            self.methods_entry_valid = True

        else:
            try:
                json_value = ast.literal_eval(value)

                self.methods_entry_valid = True if isinstance(json_value, dict) else False

            except SyntaxError:
                self.methods_entry_valid = False

        entry.config(foreground=u'black' if self.methods_entry_valid else u'red')

        return self.methods_entry_valid

    def _validate_parameters_entry(self,
                                   value):

        logging.debug(u'Validating parameters entry')

        entry = getattr(self.frames[u'add_edit_api_env_entry_frame'], u'_parameters_entry')

        if value == u'':
            self.parameters_entry_valid = True

        else:
            try:
                json_value = ast.literal_eval(value)

                self.parameters_entry_valid = True if isinstance(json_value, dict) else False

            except ValueError:
                self.parameters_entry_valid = False

        entry.config(foreground=u'black' if self.parameters_entry_valid else u'red')

        return self.parameters_entry_valid

    # Button methods
    def add_api(self):
        self.update_layout(ADD_LAYOUT)

    def delete_api(self):
        selected = self.selected.get()
        logging.debug(u'DELETE API: {d}'.format(d=selected))

        if len(self.cfg[APIS_CONFIG]) <= 1:
            showerror(u'Delete API',
                      u'Cannot remove last API!',
                      parent=self)

        elif len(self.endpoints.get_endpoints_for_api(selected)) > 0:
            showerror(u'Delete API',
                      u'Cannot remove, API used in endpoint config!',
                      parent=self)

        else:
            result = askquestion(u"Delete API",
                                 u"Are you sure you want to delete: {item}?".format(item=selected),
                                 parent=self)

            if result == u'yes':

                key = u'{k}.{a}'.format(k=APIS_CONFIG,
                                        a=self.selected.get())

                del self.cfg[key]

                self.return_to_root_layout()

    def add_edit_api_env(self):

        api = self.combo_selected.get()
        env = self.selected_env.get()
        key = u'{k}.{a}.{e}'.format(k=APIS_CONFIG,
                                    a=api,
                                    e=env)

        self.item_dict_name = api
        self.item_dict = self.cfg[key]

        self.update_layout(ADD_EDIT_ENV_LAYOUT)

        self.selected.set(env)
        self.combo_selected.set(env)

    def delete_api_env(self):
        selected_env = self.selected_env.get()
        selected_api = self.selected.get()
        logging.debug(u'DELETE API ENV: {a}:{e}'.format(a=selected_api,
                                                        e=selected_env))

        api_key = u'{k}.{a}'.format(k=APIS_CONFIG,
                                    a=selected_api)

        if len(self.cfg[api_key]) <= 1:
            showerror(u'Delete API Environment',
                      u'Cannot remove last API environment!',
                      parent=self)

        elif self.endpoints.environment_and_api_are_used_by_an_endpoint(selected_api, selected_env):
            showerror(u'Delete API Environment',
                      u'Cannot remove, API environment used in endpoint config!',
                      parent=self)

        else:
            result = askquestion(u"Delete API Environment",
                                 u"Are you sure you want to delete: {item}?".format(item=selected_env),
                                 parent=self)

            if result == u'yes':
                key = u'{k}.{e}'.format(k=api_key,
                                        e=selected_env)

                del self.cfg[key]

                self.item_dict = self.cfg[api_key]

                self.refresh()

    def cancel(self):
        self.return_to_root_layout()

    def save_api(self):

        if self.add_api_entry_valid:

            frame = self.frames[u'add_api_frame']
            entry_var = getattr(frame, u'_api_name_entry_var')

            api = entry_var.get()

            self.item_dict_name = api
            self.item_dict = {}

            self.update_layout(ADD_EDIT_ENV_LAYOUT)

            self.selected.set(u'')
            self.combo_selected.set(u'')

    def save_env(self):
        # Check env is not blank
        if self.combo_selected.get() == u'':
            self.return_to_root_layout()

        frame = self.frames[u'add_edit_api_env_entry_frame']

        self._validate_methods_entry(getattr(frame, u'_methods_entry_var').get())
        self._validate_parameters_entry(getattr(frame, u'_parameters_entry_var').get())

        if self.parameters_entry_valid and self.methods_entry_valid:
            env_config = {}

            def _env_config(key, value):
                val = getattr(frame, value).get()
                if val != u'':
                    env_config[key] = val

            _env_config(APIConstant.key, u'_key_entry_var')
            _env_config(APIConstant.secret, u'_secret_entry_var')
            _env_config(APIConstant.user, u'_user_entry_var')
            _env_config(APIConstant.password, u'_password_entry_var')
            _env_config(APIConstant.methods, u'_methods_entry_var')
            _env_config(APIConstant.params, u'_parameters_entry_var')

            if self.item_dict_name in self.cfg[APIS_CONFIG].keys():
                api_key = u'{k}.{a}.{e}'.format(k=APIS_CONFIG,
                                                a=self.item_dict_name,
                                                e=self.combo_selected.get())

                self.cfg[api_key] = env_config

            else:
                api_key = u'{k}.{a}'.format(k=APIS_CONFIG,
                                            a=self.item_dict_name)

                self.cfg[api_key] = {
                    self.combo_selected.get(): env_config
                }

            self.return_to_root_layout()
