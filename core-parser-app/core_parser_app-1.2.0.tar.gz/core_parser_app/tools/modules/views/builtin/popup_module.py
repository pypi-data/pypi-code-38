""" Pop up module
"""
from abc import ABCMeta, abstractmethod

from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractPopupModule(AbstractModule):
    """Popup module
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), button_label=''):
        """ Initialize module

        Args:
            scripts:
            styles:
        """
        scripts = ['core_parser_app/js/builtin/popup.js'] + scripts
        AbstractModule.__init__(self, scripts=scripts, styles=styles)

        self.button_label = button_label
        self.popup_content = ''

    def _render_module(self, request):
        """ Return module's rendering

        Args:
            request:

        Returns:

        """
        params = {
            "popup_content": self._get_popup_content(),
            "button_label": self.button_label,
        }

        return AbstractModule.render_template('core_parser_app/builtin/popup.html', params)

    @abstractmethod
    def _get_popup_content(self):
        """ Process data to build the module
        """
        raise NotImplementedError("not implemented")
