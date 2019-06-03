""" Remote BLOB host module views
"""

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from core_module_blob_host_app.views.views import BlobHostModule
from core_parser_app.tools.modules.views.builtin.input_module import AbstractInputModule


class RemoteBlobHostModule(AbstractInputModule):
    def __init__(self):
        """ Initialize the module
        """
        AbstractInputModule.__init__(self, label='Enter the URL of a file:')

    def _render_module(self, request):
        """ Render module

        Args:
            request:

        Returns:

        """
        return AbstractInputModule._render_module(self, request)

    def _retrieve_data(self, request):
        """ Return module's data

        Args:
            request:

        Returns:

        """
        data = ''
        self.error = None
        if request.method == 'GET':
            if 'data' in request.GET:
                if len(request.GET['data']) > 0:
                    data = request.GET['data']
        elif request.method == 'POST':
            if 'data' in request.POST:
                url = request.POST['data']
                url_validator = URLValidator()
                try:
                    url_validator(url)
                    data = url
                except ValidationError, e:
                    self.error = ' '.join(e.messages)

        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        return BlobHostModule.render_blob_host_data(self.data, self.error)

