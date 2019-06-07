'''Implementation of core ew widgets in terms of Jinja2 templates
'''
from __future__ import absolute_import
from __future__ import unicode_literals

from jinja2 import escape
from markupsafe import Markup as literal

from . import fields
from . import select
from . import forms
from . import widget
from . import resource
from .render import Snippet, File

BOOLEAN_ATTRS=set([
        'checked',
        'disabled',
        'readonly',
        'multiple',
        'selected',
        'nohref',
        'ismap',
        'declare',
        'defer',
        'required',
        'autofocus',
])


# jinja2's escape (which is really markupsafe's) already does everything we need:
#   tries __html__ for literal/Markupsafe objects
#   converts to text type
#   and escapes
_escape = escape

def _attr(k,v):
    if k.lower() in BOOLEAN_ATTRS:
        return _escape(k)
    else:
        return '%s="%s"' % (
            _escape(k), _escape(v)) 

class _Jinja2Widget(fields.FieldWidget):

    def j2_attrs(self, *attrdicts):
        attrdict={}
        for ad in attrdicts:
            if ad:
                attrdict.update(ad)
        result = [
            _attr(k,v)
            for k,v in sorted(attrdict.items())
            if v is not None ]
        return literal(' '.join(result))

#################
## Overrides from ew.fields
#################

class InputField(fields.InputField, _Jinja2Widget):
    template=Snippet('''<input {{widget.j2_attrs({
    'id':id,
    'type':field_type,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly,
    'value':value},
    attrs)}}>''', 'jinja2')

class HiddenField(fields.HiddenField, _Jinja2Widget):
    template=InputField.template

class FileField(fields.FileField, _Jinja2Widget):
    # same as above, but no "value"
    template=Snippet('''<input {{widget.j2_attrs({
    'id':id,
    'type':field_type,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly},
    attrs)}}>''', 'jinja2')

class CompoundField(fields.CompoundField, _Jinja2Widget):
    template=InputField.template

class FieldSet(fields.FieldSet, _Jinja2Widget):
    template=File('ew.templates.jinja2.field_set', 'jinja2')

class RowField(fields.RowField, _Jinja2Widget):
    template=File('ew.templates.jinja2.row_field', 'jinja2')

class RepeatedField(fields.RepeatedField, _Jinja2Widget):
    template=File('ew.templates.jinja2.repeated_field', 'jinja2')

class TableField(fields.TableField, _Jinja2Widget):
    template=File('ew.templates.jinja2.table_field', 'jinja2')
TableField.RowField=RowField

class TextField(fields.TextField, _Jinja2Widget): 
    template=InputField.template

class PasswordField(fields.PasswordField, _Jinja2Widget): 
    template=InputField.template

class EmailField(fields.EmailField, _Jinja2Widget):
    template=InputField.template

class NumberField(fields.NumberField, _Jinja2Widget):
    template=InputField.template

class IntField(fields.IntField, _Jinja2Widget):
    template=InputField.template

class DateField(fields.DateField, _Jinja2Widget):
    template=InputField.template

class TimeField(fields.TimeField, _Jinja2Widget):
    template=InputField.template

class TextArea(fields.TextArea, _Jinja2Widget):
    template=Snippet('''<textarea {{widget.j2_attrs({
    'id':id,
    'name':rendered_name,
    'class':css_class,
    'readonly':readonly},
    attrs)}}>{% if value %}{{value|e}}{% endif %}</textarea>''', 'jinja2')

class Checkbox(fields.Checkbox, _Jinja2Widget):
    template=File('ew.templates.jinja2.checkbox', 'jinja2')

class SubmitButton(fields.SubmitButton, _Jinja2Widget):
    template=Snippet('''<input {{widget.j2_attrs({
    'type':'submit',
    'name':rendered_name,
    'value':label,
    'class':css_class},
    attrs)}}>''', 'jinja2')

class HTMLField(fields.HTMLField, _Jinja2Widget):
    template=Snippet('''{% if text %}{{widget.expand(text)|safe}}
    {%- elif value %}{{value | safe}}{% endif %}''', 'jinja2')

class LinkField(fields.LinkField, _Jinja2Widget):
    '''
    Jinja2 implementation of LinkField which allows a mapping value which
    contains the href and text values separately, as well as a flag to render
    the field as plaintext if no href value is specified.  Both the href and
    text values will be escaped properly (NB: this differs from the previous
    implementation which explicitly used widget.expand(), so older code may
    need to be changed).

    The HREF of the link will be first one of value['href'], attrs['href'],
    href, or value (if value is not a mapping) that is set.

    The text of the link will be first one of value['text'], text, label, or
    value (if value is not a mapping) that is set.

    If plaintext_if_no_href is True and none of value['href'], attrs['href'],
    nor href are set, then the field will be rendered as plaintext using the
    text of the link, above.

    Examples:

        This renders as: <a href="http://example.com/">http://example.com/</a>

            LinkField().display(value="http://example.com/")

        The following all render as: <a href="/foo">bar</a>

            LinkField(href='/foo').display(value='bar')
            LinkField(text='bar').display(value='/foo')
            LinkField().display(value=dict(href='/foo', text='bar'))
            LinkField(label='bar').display(value=dict(href='/foo'))
            LinkField(href='/foo').display(value=dict(text='bar'))
            LinkField(attrs={'href':'/foo'}).display(value='bar')
            LinkField(plaintext_if_no_href=True).display(value=dict(href='/foo', text='bar'))
            LinkField(plaintext_if_no_href=True).display(href='/foo', value='bar')

        These render as the plaintext: bar

            LinkField(plaintext_if_no_href=True).display(value=dict(text='bar'))
            LinkField(plaintext_if_no_href=True, label='bar').display(value=dict())
            LinkField(plaintext_if_no_href=True, label='foo').display(value='bar')
    '''
    template=Snippet('''{% if plaintext_if_no_href and not (value['href'] or attrs['href'] or href) -%}
            {{ (value['text'] or (value is not mapping and value or None) or text or label)|e }}
        {%- elif value is mapping -%}
            <a {{ widget.j2_attrs({'href':value['href'] or href}, attrs) }}>{{ (value['text'] or text or label)|e }}</a>
        {%- else -%}
            <a {{ widget.j2_attrs({'href':href or value}, attrs) }}>{{ (text or label or value)|e }}</a>
        {%- endif %}''', 'jinja2')
    defaults=dict(
        fields.LinkField.defaults,
        value=None,
        plaintext_if_no_href=False)

#################
## Overrides from ew.select
#################

class SelectField(select.SelectField, _Jinja2Widget):
    template=File('ew.templates.jinja2.select_field', 'jinja2')

class SingleSelectField(select.SingleSelectField, _Jinja2Widget):
    template=SelectField.template

class MultiSelectField(select.MultiSelectField, _Jinja2Widget):
    template=SelectField.template

class Option(select.Option, _Jinja2Widget):
    template=Snippet('''<option {{widget.j2_attrs({
      'value':html_value,
      'selected':selected and 'selected' or None})}}>
     {{label|e}}</option>''', 'jinja2')

class CheckboxSet(select.CheckboxSet, _Jinja2Widget):
    template=File('ew.templates.jinja2.checkbox_set', 'jinja2')

#################
## Overrides from ew.forms
#################

class SimpleForm(forms.SimpleForm, _Jinja2Widget):
    template=File('ew.templates.jinja2.simple_form', 'jinja2')
SimpleForm.SubmitButton=SubmitButton

#################
## Overrides from ew.resource
#################

class JSLink(resource.JSLink):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('<script type="text/javascript" src="{{widget.href}}"></script>',
                         'jinja2')

class CSSLink(resource.CSSLink):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('''<link rel="stylesheet"
                type="text/css"
                href="{{widget.href}}"
                {{widget.j2_attrs(widget.attrs)}}>''', 'jinja2')

class JSScript(resource.JSScript):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet(
            '<script type="text/javascript">{{widget.text}}</script>',
            'jinja2')

class CSSScript(resource.CSSScript):
    class WidgetClass(_Jinja2Widget): 
        template=Snippet('<style>{{widget.text}}</style>', 'jinja2')

class GoogleAnalytics(resource.GoogleAnalytics):
    class WidgetClass(_Jinja2Widget): 
        template=File('ew.templates.jinja2.google_analytics', 'jinja2')
