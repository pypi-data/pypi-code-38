from __future__ import absolute_import
from __future__ import unicode_literals
from itertools import chain

from formencode import schema as fes

from . import fields
from .render import File

class SimpleForm(fields.CompoundField):
    template=File('ew.templates.simple_form')
    defaults=dict(
        fields.CompoundField.defaults,
        method='POST',
        action=None,
        submit_text='Submit',
        buttons=[],
        extra_fields=[],
        enctype=None,
        attrs=None,
        show_label=False)
    SubmitButton = fields.SubmitButton

    def __init__(self, **kw):
        super(SimpleForm, self).__init__(**kw)

    def prepare_context(self, context):
        result = super(SimpleForm, self).prepare_context(context)
        if result['submit_text'] is not None:
            b = self.SubmitButton(label=result['submit_text'])
            result['buttons'] = [b] + result['buttons']
        result['extra_fields'] += result['buttons']
        return result

    def _all_fields(self):
        return chain(super(SimpleForm, self)._all_fields(), self.buttons)

    def _make_schema(self):
        base_schema = super(SimpleForm, self)._make_schema()
        if self.name:
            return fes.Schema(**{self.name:base_schema,
                             'allow_extra_fields':True,
                             'filter_extra_fields':True})
        else:
            return base_schema
