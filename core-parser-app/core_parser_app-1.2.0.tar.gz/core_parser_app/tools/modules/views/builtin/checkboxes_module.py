""" Checkboxes Module
"""
from abc import ABCMeta
from math import ceil

from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.module import AbstractModule


class AbstractCheckboxesModule(AbstractModule):
    """ Checkboxes module
    """
    __metaclass__ = ABCMeta

    def __init__(self, scripts=list(), styles=list(), label=None, name=None, options=None, selected=list()):
        """ Initialize the module

        Args:
            scripts:
            styles:
            label:
            name:
            options:
            selected:
        """
        scripts = ['core_parser_app/js/builtin/checkboxes.js'] + scripts
        styles = ['core_parser_app/css/builtin/checkboxes.css'] + styles
        AbstractModule.__init__(self, scripts=scripts, styles=styles)

        if name is None:
            raise ModuleError("The name can't be empty.")

        self.selected = selected
        self.options = options if options is not None else dict()
        self.label = label

    # FIXME: use a template to generate the HTML of the checkbox
    @staticmethod
    def _create_html_checkbox(input_key, input_value, checked=False):
        """ Return the html of the checkboxes

        Args:
            input_key:
            input_value:
            checked:

        Returns:

        """
        input_tag = '<input type="checkbox" '
        if checked:
            input_tag += 'checked '
        input_tag += 'value="' + input_key + '"/> ' + input_value

        return '<span>' + input_tag + '</span>'

    def _render_module(self, request):
        """ Return the module

        Args:
            request:

        Returns:

        """
        # Compute number of items in each columns
        col_nb = 3
        opt_nb = len(self.options)
        max_item_nb = int(ceil(opt_nb / col_nb))

        # Parameters initialization
        params = {
            "column1": "",
            "column2": "",
            "column3": "",
        }
        item_nb = 0
        col_id = 1
        checkboxes_html = ""

        # Filling the parameters
        for key, val in self.options.items():
            if item_nb == max_item_nb:
                params['column' + str(col_id)] = checkboxes_html

                checkboxes_html = ""
                item_nb = 0
                col_id += 1

            checkboxes_html += CheckboxesModule._create_html_checkbox(key, val, checked=(key in self.selected))
            item_nb += 1

        params['column' + str(col_id)] = checkboxes_html

        if self.label is not None:
            params.update({"label": self.label})

        return AbstractModule.render_template('core_parser_app/builtin/checkboxes.html', params)
