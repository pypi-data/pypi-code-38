""" Auto keyref module views
"""
from core_module_auto_key_app.components.auto_key import api as auto_key_api
from core_module_auto_keyref_app.components.auto_keyref import api as auto_keyref_api
from core_module_auto_keyref_app.components.auto_keyref.models import AutoKeyref
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.builtin.options_module import AbstractOptionsModule


class AutoKeyRefModule(AbstractOptionsModule):
    def __init__(self):
        """ Initialize module

        """
        self.selected = None
        self.values = []
        AbstractOptionsModule.__init__(self, options={}, scripts=['core_module_auto_keyref_app/js/autokey.js'])

    def _render_module(self, request):
        """ Return module's rendering

        Args:
            request:

        Returns:

        """
        # add empty value
        self.options.update({'': ''})
        # add values to available options
        for value in self.values:
            self.options.update({str(value): str(value)})

        self.selected = self.data
        return AbstractOptionsModule._render_module(self, request)

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            # look for existing values
            try:
                # get module id
                module_id = request.GET['module_id']
                # get module element from module id
                module = data_structure_element_api.get_by_id(module_id)
                # get keyref id in moduke
                keyref_id = module.options['params']['keyref']

                # get XML document root element
                root_element = data_structure_element_api.get_root_element(module)
                try:
                    # get auto keyref manager by root
                    auto_keyref = auto_keyref_api.get_by_root(root_element)
                except:
                    # if auto keyref manager does not exist, create it
                    auto_keyref = AutoKeyref(root=root_element)
                    auto_keyref_api.upsert(auto_keyref)

                # if keyref id not already present
                if keyref_id not in auto_keyref.keyrefs.keys():
                    # initialize keyref entry
                    auto_keyref.keyrefs[keyref_id] = []

                # if module id not already registered
                if str(module_id) not in auto_keyref.keyrefs[keyref_id]:
                    # add module id to keyref manager
                    auto_keyref.keyrefs[keyref_id].append(str(module_id))

                # update auto keyref
                auto_keyref_api.upsert(auto_keyref)

                # get key id from root element
                key_id = root_element.options['keyrefs'][keyref_id]['refer']

                try:
                    # get auto key
                    auto_key = auto_key_api.get_by_root(root_element)
                    # get list of module ids for the given key id
                    modules_ids = auto_key.keys[key_id]
                except:
                    # no auto key found, create an empty list of module ids
                    modules_ids = []

                self.values = []
                for key_module_id in modules_ids:
                    key_module = data_structure_element_api.get_by_id(key_module_id)
                    if key_module.options['data'] is not None:
                        self.values.append(key_module.options['data'])

                # get data from request
                if 'data' in request.GET:
                    data = request.GET['data']
                # get data from db
                elif 'data' in module.options and module.options['data'] is not None:
                    data = str(module.options['data'])
            except Exception, e:
                raise ModuleError("An unexpected error occurred in AutoKeyrefModule: " + e.message)

        elif request.method == 'POST':
            if 'data' in request.POST:
                data = request.POST['data']

        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        return ''
