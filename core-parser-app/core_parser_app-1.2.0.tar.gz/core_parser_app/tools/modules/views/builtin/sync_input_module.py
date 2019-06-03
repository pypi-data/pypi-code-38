""" Synchronous Input Module
"""
from abc import ABCMeta

from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractSyncInputModule(AbstractModule):
    """Synchronous input module
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), label=None, default_value=None, modclass=None, disabled=False):
        """ Initialize the module

        Args:
            scripts:
            styles:
            label:
            default_value:
            modclass:
            disabled:
        """
        scripts = ['core_parser_app/js/builtin/sync_input.js'] + scripts
        AbstractModule.__init__(self, scripts=scripts, styles=styles)

        if modclass is None:
            raise ModuleError("'modclass' is required.")

        self.modclass = modclass
        self.label = label
        self.default_value = default_value
        self.disabled = disabled

    def _render_module(self, request):
        """ Return module's rendering

        Args:
            request:

        Returns:

        """

        params = {'class': self.modclass}
        if self.label is not None:
            params.update({"label": self.label})
        if self.default_value is not None:
            params.update({"default_value": self.default_value})
        if self.disabled is not None:
            params.update({"disabled": self.disabled})
        return AbstractModule.render_template('core_parser_app/builtin/sync_input.html', params)
