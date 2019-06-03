""" Status registry Module
"""
from core_parser_app.tools.modules.views.builtin.options_module import AbstractOptionsModule
from core_main_registry_app.commons.constants import DataStatus


class StatusRegistryModule(AbstractOptionsModule):
    def __init__(self):
        self.options = {
            DataStatus.INACTIVE: 'Inactive',
            DataStatus.ACTIVE: 'Active',
        }

        AbstractOptionsModule.__init__(self, options=self.options, disabled=True)

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """

        data = DataStatus.ACTIVE
        self.selected = DataStatus.ACTIVE
        if request.method == 'GET':
            if 'data' in request.GET:
                self.disabled = False
                self.selected = request.GET['data']
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
