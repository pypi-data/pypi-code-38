""" Auto Key module
"""
from core_module_auto_key_app.components.auto_key import api as auto_key_api
from core_module_auto_key_app.components.auto_key.models import AutoKey
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.builtin.sync_input_module import AbstractSyncInputModule


class AutoKeyModule(AbstractSyncInputModule):
    """ Auto Key module
    """

    def __init__(self, key_gen_func):
        """Initializes the module

        """
        if key_gen_func is None:
            raise ModuleError('A function for the generation of the keys should be provided (key_gen_func is None).')

        self.key_gen_func = key_gen_func
        AbstractSyncInputModule.__init__(self, modclass='mod_auto_key', disabled=True)

    def _render_module(self, request):
        """ Returns the module

        Args:
            request:

        Returns:

        """
        self.default_value = self.data
        return AbstractSyncInputModule._render_module(self, request)

    def _retrieve_data(self, request):
        """

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            try:
                # get module id
                module_id = request.GET['module_id']
                # get module element form module id
                module = data_structure_element_api.get_by_id(module_id)
                # get key id form module
                key_id = module.options['params']['key']

                # get XML document root element from module element
                root_element = data_structure_element_api.get_root_element(module)
                try:
                    # get auto key manager from db
                    auto_key = auto_key_api.get_by_root(root_element)
                except:
                    # create auto key manager if doesn't exist
                    auto_key = AutoKey(root=root_element)
                    auto_key_api.upsert(auto_key)

                # if key id not already present in auto key manager
                if key_id not in auto_key.keys.keys():
                    # initialize key id entry
                    auto_key.keys[key_id] = []

                # if module id not already present in auto key manager
                if str(module_id) not in auto_key.keys[key_id]:
                    # add module id to auto key manager
                    auto_key.keys[key_id].append(str(module_id))

                # update auto key
                auto_key_api.upsert(auto_key)

                # if data are present
                if 'data' in request.GET:
                    # set the key coming from data
                    data = request.GET['data']
                else:
                    # get the list of values for this key
                    values = []
                    module_ids = auto_key.keys[key_id]
                    for key_module_id in module_ids:
                        try:
                            key_module = data_structure_element_api.get_by_id(key_module_id)
                            if key_module.options['data'] is not None:
                                values.append(key_module.options['data'])
                        except:
                            pass

                    # generate next key
                    data = str(self.key_gen_func(values))
            except Exception, e:
                raise ModuleError("An unexpected error occurred in AutoKeyModule: " + e.message)

        return data

    def _render_data(self, request):
        """

        Args:
            request:

        Returns:

        """
        return ''
