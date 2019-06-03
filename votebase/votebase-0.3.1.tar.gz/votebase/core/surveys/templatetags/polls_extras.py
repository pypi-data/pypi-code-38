import urllib

from django import template
from django.forms.widgets import Select, SelectMultiple, Textarea, TextInput, CheckboxInput, PasswordInput
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter(name='field_type')
def field_type(arg):
    if isinstance(arg, str):
        return 'type-undefined'
    
    if type(arg.field.widget) is Select:
        return 'type-select'
    elif type(arg.field.widget) is SelectMultiple:
        return 'type-select-multiple'
    elif type(arg.field.widget) is TextInput:
        return 'type-input'
    elif type(arg.field.widget) is Textarea:
        return 'type-textarea'
    elif type(arg.field.widget) is CheckboxInput:
        return 'type-checkbox'
    elif type(arg.field.widget) is PasswordInput:
        return 'type-password'

    return 'type-undefined'

@register.filter
@stringfilter
def qrcode(value, alt=None):
    """
    Generate QR Code image from a string with the Google charts API

    http://code.google.com/intl/fr-FR/apis/chart/types.html#qrcodes

    Exemple usage --
    {{ my_string|qrcode:"my alt" }}

    <img src="http://chart.apis.google.com/chart?chs=150x150&amp;cht=qr&amp;chl=my_string&amp;choe=UTF-8" alt="my alt" />
    """

    url = conditional_escape("http://chart.apis.google.com/chart?%s" %
                             urllib.urlencode({'chs': '250x250', 'cht': 'qr', 'chl': value, 'choe': 'UTF-8'}))
    alt = conditional_escape(alt or value)

    return mark_safe(u"""<img class="qrcode" src="%s" width="250" height="250" alt="%s" />""" % (url, alt))


@register.filter()
def user_already_voted(segment, user):
    return segment.user_already_voted(user)
