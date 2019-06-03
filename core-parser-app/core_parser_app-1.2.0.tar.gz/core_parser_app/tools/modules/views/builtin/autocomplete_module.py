"""Auto Complete Module
"""
from abc import ABCMeta

from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractAutoCompleteModule(AbstractModule):
    """ AutoCompleteModule class
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), label=None):
        """ Initialize the module

        Args:
            scripts:
            styles:
            label:
        """
        scripts = ['core_parser_app/js/builtin/autocomplete.js'] + scripts
        AbstractModule.__init__(self, scripts=scripts, styles=styles)

        self.label = label

    def _render_module(self, request):
        """ Return the module

        Args:
            request:

        Returns:

        """
        params = {}

        if self.data != '':
            params['value'] = self.data

        if self.label is not None:
            params.update({"label": self.label})

        return AbstractModule.render_template('core_parser_app/builtin/autocomplete.html', params)
