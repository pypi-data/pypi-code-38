""" Input Button Module
"""
from abc import ABCMeta

from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractInputButtonModule(AbstractModule):
    """ Input Button module
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), button_label='Send', label=None, default_value=None):
        """ Initialize the module

        Args:
            scripts:
            styles:
            button_label:
            label:
            default_value:
        """
        AbstractModule.__init__(self, scripts=scripts, styles=styles)
        self.button_label = button_label
        self.label = label
        self.default_value = default_value

    def _render_module(self, request):
        """ Return the module rendering

        Args:
            request:

        Returns:

        """
        params = {"button_label": self.button_label}
        if self.label is not None:
            params.update({"label": self.label})
        if self.default_value is not None:
            params.update({"default_value": self.default_value})
        return AbstractModule.render_template('core_parser_app/builtin/input_button.html', params)

