from __future__ import absolute_import
from __future__ import unicode_literals
from itertools import chain
import traceback
import warnings

import six
from formencode import schema as fes
from formencode.foreach import ForEach
from formencode import validators as fev

from .validators import TimeConverter, DateConverter, UnicodeString
from .widget import Widget
from .utils import Bunch, safe_getitem
from . import core


class EasyWidgetsWarning(UserWarning):
    pass


class FieldWidget(Widget, fev.Validator):
    '''Widget that also functions as a validator.  Base class for all Form Field
    widgets.'''
    perform_validation=True
    validator=None

    @core.validator
    def validate(self, value, state):
        return self.to_python(value, state)

    @core.validator
    def to_python(self, value, state):
        if self.perform_validation and self.validator:
            return self.validator.to_python(value, state)
        return value
    
    def from_python(self, value, state):
        if self.perform_validation and self.validator:
            if isinstance(self.validator, fev.UnicodeString):
                # we don't want to encode u'foo' into bytes, or b'foo' will start showing up places
                self.validator.outputEncoding = None
            return self.validator.from_python(value, state)
        return value
    
    def prepare_context(self, context):
        context = super(FieldWidget, self).prepare_context(context)
        # before py3 conversions, if context['value'] was missing, that would raise an IndexError,
        # and this function trapped all errors, so it wouldn't change its value
        # so we preserve that resulting behavior (unset stays unset)
        if 'value' in context:
            try:
                context['value'] = self.from_python(context['value'], None)
            except Exception as e:
                warnings.warn('suppressed an error that you should probably fix. ' + traceback.format_exc(e),
                              EasyWidgetsWarning,
                              stacklevel=4,
                              )
        return context

class InputField(FieldWidget):
    _ordinal = 0
    defaults=dict(
        FieldWidget.defaults,
        id=None,
        name=None,
        rendered_name=None,
        label=None,
        value=None,
        errors=None,
        attrs=None,
        readonly=None,
        field_type=None,
        css_class=None,
        show_label=True,
        show_errors=True)
    validator = None
    perform_validation = True

    def __init__(self, **kw):
        self._if_missing = ()
        super(InputField, self).__init__(**kw)
        if self.label is None and self.name:
            self.label = self.name.capitalize()
        if self.validator and getattr(self.validator, 'not_empty', False) == True:
            if self.attrs and 'required' not in self.attrs:
                self.attrs['required'] = True

    def _get_if_missing(self):
        if self._if_missing == ():
            return self.validator.if_missing
        else:
            return self._if_missing
    def _set_if_missing(self, value):
        self._if_missing = value
    if_missing = property(_get_if_missing, _set_if_missing)

    def prepare_context(self, context):
        response = super(InputField, self).prepare_context(context)
        if response.get('id') is None:
            response['id'] = 'w-%x' % InputField._ordinal
            InputField._ordinal += 1
        if response.get('rendered_name') is None:
            response['rendered_name'] = response.get('name')
        return response

class HiddenField(InputField):
    defaults=dict(
        InputField.defaults,
        show_label=False,
        show_errors=False,
        field_type='hidden')

class FileField(InputField):
    defaults=dict(
        InputField.defaults,
        field_type='file',
    )

class CompoundField(InputField):
    defaults=dict(
        InputField.defaults,
        errors=None,
        hidden_fields=[],
        extra_fields=[],
        show_labels=True,
        error_class='fielderror')
    fields=[]
    chained_validators = []

    @core.validator
    def to_python(self, value, state=None):
        schema = self._make_schema()
        result =  schema.to_python(value, state)
        return result

    def from_python(self, value, state=None):
        if value is None: return None
        try:
            if not hasattr(value, 'iteritems'):
                names = [ f.name for f in self.fields ]
                value = dict((k, getattr(value, k))
                             for k in names)
            result = self._make_schema().from_python(value, state)
            d = dict(value)
            d.update(result)
            return d
        except:
            return value

    def resources(self):
        for f in chain(self.fields, self.hidden_fields, self.extra_fields):
            for r in f.resources(): yield r

    def prepare_context(self, context):
        response = super(CompoundField, self).prepare_context(context)
        err = core.widget_context.validation_error
        if response.get('errors', None) is None and err:
            response['errors'] = err.unpack_errors()
            response['value'] = err.value
            if getattr(self, 'name', None):
                response['errors'] = response['errors'].get(self.name, None)
                response['value'] = response['value'].get(self.name, None)
        return response

    def context_for(self, field):
        context = core.widget_context.render_context
        if not field.name:
            return Bunch(
                id=context.get('id', None),
                name=context.get('name', None),
                rendered_name=context.get('rendered_name', None),
                value=context.get('value', None),
                errors=context.get('errors', None))
        if context.get('name'):
            name = context['name'] + '.' + field.name
        else:
            name = field.name
        id = context['id'] + '.' + field.name
        r = Bunch(
            id=id,
            name=name,
            rendered_name=name,
            value=safe_getitem(context, 'value', field.name),
            errors=safe_getitem(context, 'errors', field.name))
        return r

    def _all_fields(self):
        return chain(self.fields, self.hidden_fields, self.extra_fields)

    def _make_schema(self):
        kwargs = dict((f.name, f) for f in self._all_fields()
                      if f.name and getattr(f, 'perform_validation', False))
        for f in self.fields:
            if f.name: continue
            if hasattr(f, '_make_schema'):
                kwargs.update(f._make_schema().fields)
        kwargs.update(chained_validators=self.chained_validators,
                      ignore_key_missing=True,
                      allow_extra_fields=True,
                      filter_extra_fields=True)
        return fes.Schema(**kwargs)

class FieldSet(CompoundField):
    defaults=dict(
        CompoundField.defaults,
        show_label=False)

class RowField(CompoundField): pass

class RepeatedField(InputField):
    defaults=dict(
        InputField.defaults,
        errors=None,
        repetitions=3,
        error_class='fielderror')
    field=None
    chained_validators = []

    def __init__(self, **kw):
        self._name = None
        super(RepeatedField, self).__init__(**kw)

    @core.validator
    def to_python(self, value, state=None):
        return self._make_schema().to_python(value, state)

    def from_python(self, value, state=None):
        if value is None: return None
        return self._make_schema().from_python(value, state)

    def resources(self):
        return self.field.resources()

    def prepare_context(self, context):
        response = super(RepeatedField, self).prepare_context(context)
        err = core.widget_context.validation_error
        if response.get('errors', None) is None and err:
            response['errors'] = err.unpack_errors()
            response['value'] = err.value
        if response.get('value', None) is not None:
            response['repetitions'] = len(response['value'])
        else:
            response['value'] = [ None ] * response['repetitions']
        return response

    def context_for(self, repetition):
        def get(coll, default=None):
            try:
                return coll[repetition]
            except (IndexError, KeyError):
                return default
        context = core.widget_context.render_context
        value = context.get('value') or []
        name = context['name'] + '-' + six.text_type(repetition)
        id = context['id'] + '-' + six.text_type(repetition)
        r = Bunch(
            id=id,
            rendered_name=name,
            name=name,
            value=get(value, None),
            errors=None)
        if context.get('errors', None) is not None:
            r['errors'] = get(context['errors']) or {}
        return r

    def _get_name(self):
        if self._name is None:
            if self.field: return self.field.name
            else: return self._name
        return self._name
    def _set_name(self, value):
        self._name = value
    name = property(_get_name, _set_name)

    def _make_schema(self):
        return ForEach(self.field, if_missing=[], if_empty=[])

class TableField(RepeatedField):
    show_label = False
    fields=[]
    hidden_fields=[]
    RowField=RowField

    def __init__(self, **kw):
        super(TableField, self).__init__(**kw)
        if self.field is None:
            fields = kw.get('fields', self.fields)
            hidden_fields = kw.get('hidden_fields', self.hidden_fields)
            name = self.name
            self.field = self.RowField(name=name, fields=fields, hidden_fields=hidden_fields)
            self.name = None

    def context_for(self, repetition):
        context = core.widget_context.render_context
        result = super(TableField, self).context_for(repetition)
        result['id'] = context['id'] + '-row-' + six.text_type(repetition)
        return result

class TextField(InputField):
    validator = UnicodeString()
    defaults=dict(
        InputField.defaults,
        field_type='text')

class PasswordField(TextField):
    defaults=dict(
        TextField.defaults,
        field_type='password')

class EmailField(TextField):
    validator = fev.Email()

class NumberField(TextField):
    validator = fev.Number()

class IntField(TextField):
    validator = fev.Int()

class DateField(TextField):
    validator=DateConverter()
    defaults=dict(
        TextField.defaults,
        attrs={'style':'width:6em'})

class TimeField(TextField):
    validator=TimeConverter(use_seconds=False)
    defaults=dict(
        TextField.defaults,
        attrs={'style':'width:5em'})

class TextArea(InputField):
    validator = UnicodeString()
    defaults=dict(
        InputField.defaults,
        cols=60)

class Checkbox(InputField):
    validator=fev.StringBool(if_empty=False, if_missing=False)
    defaults=dict(
        InputField.defaults,
        show_label=False, # don't show default label
        suppress_label=False, # if true, don't label the checkbox
        )

    def from_python(self, value, state):
        if value: return 'CHECKED'
        else: return None

class SubmitButton(InputField):
    validator=UnicodeString(if_empty=None, if_missing=None)
    defaults=dict(
        InputField.defaults,
        show_label=False,
        css_class='submit')

class HTMLField(Widget):
    defaults=dict(
        Widget.defaults,
        show_label=False,
        show_errors=False,
        text='')
    perform_validation=False

class LinkField(Widget):
    defaults=dict(
        Widget.defaults,
        href=None,
        attrs=None,
        label=None,
        text=None,
        show_label=False)

    
