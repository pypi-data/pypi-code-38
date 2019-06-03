import datetime

from django import forms
from django.conf import settings


class PickadayFormMixin(object):
    def fix_fields(self, *args, **kwargs):
        for field_name in self.fields:
            if isinstance(self.fields[field_name], forms.fields.DateField):
                self.fix_field(field_name, *args, **kwargs)

    def fix_field(self, field_name, *args, **kwargs):
        date = None
        full_field_name = field_name
        prefix = kwargs.get('prefix', None)

        if prefix:
            full_field_name = '%s-%s' % (prefix, field_name)

        if full_field_name in self.data:
            date = self.data.get(full_field_name)
        elif 'initial' in kwargs and full_field_name in kwargs.get('initial'):
            date = kwargs.get('initial').get(full_field_name)

        if not date and kwargs.get('instance', None) is not None:
            instance = kwargs.get('instance')
            date = getattr(instance, full_field_name)

        if date:
            if type(date) == datetime.date:
                date = date.strftime(settings.DATE_FORMAT)
            self.fields[field_name].widget.attrs['data-value'] = date
