from __future__ import absolute_import
from django.forms import *  # NOQA


class NullBooleanSelect(NullBooleanSelect):
    def __init__(self, *args, **kw):
        super(NullBooleanSelect, self).__init__(*args, **kw)
        self.choices = (
                (u'', 'Unknown'),
                (u'1', 'Yes'),
                (u'0', 'No'))

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value is None or value == '':
            return None
        if value in ('True', 'true', '1', 1):
            return True
        return False


class NullBooleanField(NullBooleanField):
    widget = NullBooleanSelect


class BooleanField(BooleanField):
    widget = NullBooleanSelect

    def to_python(self, value):
        """Returns a Python boolean object."""
        if isinstance(value, basestring) and value.lower() in ('false', '0'):
            value = False
        else:
            if value is not None:
                value = bool(value)
        return value

    def validate(self, value):
        if value is None and self.required:
            raise ValidationError(self.error_messages['required'])


class ISODateField(DateTimeField):

    def strptime(self, value, format):
        import dateutil
        return dateutil.parser.parse(value)


class RestFormMixin:
    def _clean_fields(self):
        for name, field in self.fields.items():
            key = self.add_prefix(name)
            if not field.required and key not in self.data:
                continue

            value = field.widget.value_from_datadict(
                    self.data, self.files, key)
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]


class ModelForm(RestFormMixin, ModelForm):
    pass


class Form(RestFormMixin, Form):
    pass
