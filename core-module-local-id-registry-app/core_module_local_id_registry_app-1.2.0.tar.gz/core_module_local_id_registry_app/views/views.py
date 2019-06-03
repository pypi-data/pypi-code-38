""" Local Id Registry Module
"""
from core_main_registry_app.components.data.api import generate_unique_local_id
from core_module_local_id_registry_app.settings import LOCAL_ID_LENGTH
from core_parser_app.tools.modules.views.builtin.input_module import AbstractInputModule


class LocalIdRegistryModule(AbstractInputModule):
    def __init__(self):
        """ Initialize module
        """
        AbstractInputModule.__init__(self, disabled=True)

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            if 'data' in request.GET:
                data = request.GET['data']
            else:
                data = generate_unique_local_id(LOCAL_ID_LENGTH)
            self.default_value = data
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
