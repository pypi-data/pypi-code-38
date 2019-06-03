"""Base Renderer class
"""
import types
from os.path import join

from django.template import loader
from django.template.backends.django import Template

from core_parser_app.components.data_structure_element.models import DataStructureElement


class DefaultRenderer(object):

    def __init__(self, xsd_data, template_list=None):
        """Default renderer for the HTML form

        Args:
            xsd_data:
            template_list:
        """

        if not isinstance(xsd_data, DataStructureElement):
            raise TypeError("xsd_data type should be a SchemaElement")

        if template_list is not None:
            if type(template_list) != dict:
                raise TypeError("template_list type is wrong (" + str(type(template_list)) + " received, dict needed")

            for template in template_list.values():
                if not isinstance(template, Template):
                    template_type = str(type(template_list))
                    raise TypeError("template value type is wrong (" + template_type + " received, dict needed")

        self.data = xsd_data
        self.warnings = []

        default_renderer_path = join('renderer', 'default')
        self.templates = {
            'form_error': loader.get_template(join(default_renderer_path, 'form-error.html')),
            'warning': loader.get_template(join(default_renderer_path, 'warning.html')),

            'input': loader.get_template(join(default_renderer_path, 'inputs', 'input.html')),
            'select': loader.get_template(join(default_renderer_path, 'inputs', 'select.html')),
            'checkbox': loader.get_template(join(default_renderer_path, 'inputs', 'checkbox.html')),
            'boolean': loader.get_template(join(default_renderer_path, 'inputs', 'boolean.html')),
            'date': loader.get_template(join(default_renderer_path, 'inputs', 'date.html')),

            'btn_add': loader.get_template(join(default_renderer_path, 'buttons', 'add.html')),
            'btn_del': loader.get_template(join(default_renderer_path, 'buttons', 'delete.html')),
            'btn_collapse': loader.get_template(join(default_renderer_path, 'buttons', 'collapse.html'))
        }

        if template_list is not None:
            self.templates.update(template_list)

    def _load_template(self, tpl_key, tpl_data=None):
        """Loads an HTML template

        Args:
            tpl_key:
            tpl_data:

        Returns:

        """
        context = {}

        if tpl_key not in self.templates.keys():
            raise IndexError('Template "' + tpl_key + '" not found in registered templates ' +
                             str(self.templates.keys()))

        if tpl_data is not None and type(tpl_data) != dict:
            raise TypeError('Data parameter should be a dict (' + str(type(tpl_data)) + ' given)')

        if tpl_data is not None:
            context.update(tpl_data)

        return self.templates[tpl_key].render(context)

    def _render_form_error(self, err_message):
        """Renders errors

        Args:
            err_message:

        Returns:

        """
        if type(err_message) not in [str, unicode]:
            raise TypeError('Error message should be string or unicode (' + str(type(err_message)) + ' given)')

        context = {}
        data = {
            'message': err_message
        }

        context.update(data)
        return self.templates['form_error'].render(context)

    def _render_warnings(self):
        """Renders warnings

        Returns:

        """
        html_content = ''

        for warning in self.warnings:
            data = {
                'message': warning
            }

            html_content += self._load_template('warning', data)

        return html_content

    def _render_input(self, element):
        """Renders a text input

        Args:
            element:

        Returns:

        """
        placeholder = ''
        tooltip = ''
        use = ''
        is_fixed = False

        if 'placeholder' in element.options:
            placeholder = element.options['placeholder']

        if 'tooltip' in element.options:
            tooltip = element.options['tooltip']

        if 'use' in element.options:
            use = element.options['use']

        if 'fixed' in element.options:
            is_fixed = element.options['fixed']

        data = {
            'id': element.pk,
            'value': element.value,
            'placeholder': placeholder,
            'tooltip': tooltip,
            'use': use,
            'fixed': is_fixed,
        }

        if 'input_type' in element.options:
            if element.options['input_type'] is not None:
                if element.options['input_type'] == 'boolean':
                    data['class'] = 'restriction'
                    return self._load_template('boolean', data)
                elif element.options['input_type'] == 'date':
                    return self._load_template('date', data)

        return self._load_template('input', data)

    def _render_select(self, select, select_class, option_list):
        """Renders a drop down list

        Args:
            select:
            select_class:
            option_list:

        Returns:

        """
        if select is None:
            select_id = ''
            is_fixed = False
        else:
            select_id = select.pk
            is_fixed = select.options['fixed'] if 'fixed' in select.options else False
        if not isinstance(option_list, types.ListType):
            raise TypeError('First param (option_list) should be a list (' + str(type(option_list)) + ' given)')

        for option in option_list:
            if not isinstance(option, types.TupleType):
                raise TypeError('Malformed param (option_list): type of item not good')

            if len(option) != 3:
                raise TypeError('Malformed param (option_list): Length of item not good')

            if type(option[0]) not in [str, unicode]:
                raise TypeError('Malformed param (option_list): item[0] should be a str')

            if type(option[1]) not in [str, unicode]:
                raise TypeError('Malformed param (option_list): item[1] should be a str')

            if type(option[2]) != bool:
                raise TypeError('Malformed param (option_list): item[2] should be a bool')

        data = {
            'select_id': select_id,
            'select_class': select_class,
            'option_list': option_list,
            'fixed': is_fixed
        }

        return self._load_template('select', data)

    def _render_buttons(self, add_button, delete_button):
        """Displays buttons for a duplicable/removable element

        Args:
            add_button:
            delete_button:

        Returns:

        """
        add_button_type = type(add_button)
        del_button_type = type(delete_button)

        if add_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(add_button_type) + 'received, bool needed')

        if del_button_type is not bool:
            raise TypeError('add_button type is wrong (' + str(del_button_type) + 'received, bool needed')

        form_string = ""

        # Fixed number of occurences, don't need buttons
        if not add_button and not delete_button:
            pass
        else:
            if add_button:
                form_string += self._load_template('btn_add', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_add', {'is_hidden': True})

            if delete_button:
                form_string += self._load_template('btn_del', {'is_hidden': False})
            else:
                form_string += self._load_template('btn_del', {'is_hidden': True})

        return form_string

    def _render_collapse_button(self):
        """Renders a collapse button

        Returns:

        """
        return self._load_template('btn_collapse')
