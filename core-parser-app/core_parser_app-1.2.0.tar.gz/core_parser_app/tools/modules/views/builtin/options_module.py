""" Options Module
"""
from abc import ABCMeta

from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractOptionsModule(AbstractModule):
    """Options Modules
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), label=None, options=None, disabled=False, selected=None):
        """ Initialize module

        Args:
            scripts:
            styles:
            label:
            options:
            disabled:
            selected:
        """
        if options is None:
            options = {}

        scripts = ['core_parser_app/js/builtin/options.js'] + scripts
        AbstractModule.__init__(self, scripts=scripts, styles=styles)

        self.options = options
        self.label = label
        self.disabled = disabled
        self.selected = selected

    def _render_module(self, request):
        """ Return module's rendering

        Args:
            request:

        Returns:

        """
        options_html = ""

        if self.selected not in self.options.keys():
            self.selected = None

        for key, val in self.options.items():
            if self.selected is not None and key == self.selected:
                options_html += "<option value='" + key + "' selected>" + val + "</option>"
            else:
                options_html += "<option value='" + key + "'>" + val + "</option>"

        params = {"options": options_html}

        if self.label is not None:
            params.update({"label": self.label})

        if self.disabled is not None:
            params.update({"disabled": self.disabled})

        return AbstractModule.render_template('core_parser_app/builtin/options.html', params)
