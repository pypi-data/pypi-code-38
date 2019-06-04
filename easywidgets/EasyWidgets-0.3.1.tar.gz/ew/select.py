from __future__ import absolute_import
from __future__ import unicode_literals

import six
from formencode import compound as fec
from formencode.foreach import ForEach

from .widget import Widget
from .fields import InputField
from .validators import OneOf, UnicodeString
from .render import File, Snippet
from . import core 

class SelectField(InputField):
    template=File('ew.templates.select_field')
    validator=UnicodeString()
    defaults=dict(
        InputField.defaults,
        options=None,
        multiple=None)

    def __init__(self, **kwargs):
        super(SelectField, self).__init__(**kwargs)

    @core.validator
    def to_python(self, value, state=None):
        schema = self._make_schema()
        result = schema.to_python(value, state)
        return result

    def from_python(self, value, state=None):
        return self._make_schema().from_python(value, state)

    def prepare_context(self, context):
        context = super(SelectField, self).prepare_context(context)
        if callable(context['options']):
            options = context['options']()
        else:
            options = context['options']
        context['options'] = [
            self._option_object_for(context['value'], o)
            for o in options ]
        return context

    def _option_object_for(self, value, option):
        if not isinstance(option, Option):
            option = Option(label=six.text_type(option), py_value=six.text_type(option))
        if option.html_value is None:
            option.html_value = self.validator.from_python(option.py_value, None)
        return option

class SingleSelectField(SelectField):

    def _option_object_for(self, value, option):
        option = super(SingleSelectField, self)._option_object_for(value, option)
        if option.html_value == value or (value is None and option.selected):
            option.selected = True
        else:
            option.selected = False
        return option

    def _make_schema(self):
        def _get_options():
            if callable(self.options):
                return self.options()
            else:
                return self.options
        oneof_validator = OneOf(
            lambda:[self._option_object_for((), o).html_value
                    for o in _get_options() ])
        return fec.All(
            self.validator,
            oneof_validator)

class MultiSelectField(SelectField):
    defaults=dict(
        SelectField.defaults,
        multiple=True)

    def _option_object_for(self, value, option):
        option = super(MultiSelectField, self)._option_object_for(value, option)
        if option.html_value in value:
            option.selected = True
        else:
            option.selected = False
        return option

    def _make_schema(self):
        if callable(self.options):
            options = self.options()
        else:
            options = self.options
        validator = fec.All(
            self.validator,
            OneOf(
                lambda:[self._option_object_for((), o).html_value
                        for o in options ]))
        return ForEach(validator, convert_to_list=True, if_empty=[], if_missing=[])

class Option(Widget):
    defaults=dict(
        Widget.defaults,
        html_value=None,
        py_value=None,
        label=None,
        selected=False)

class CheckboxSet(MultiSelectField):
    defaults=dict(
        MultiSelectField.defaults,
        show_label=False,
        option_widget=None)

