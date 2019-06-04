from math import modf

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter(is_safe=True)
def sb_currency(value):
    if not isinstance(value, int):
        try:
            value = int(value)
        except:
            value = 0
    minor, major = modf(value / 100)
    return mark_safe('%s<span>.%s</span>' % \
        (intcomma(int(major)), '{:.2f}'.format(minor)[2:]))

@register.filter(is_safe=True)
def sb_currency_text(value):
    if not isinstance(value, int):
        try:
            value = int(value)
        except:
            value = 0
    minor, major = modf(value / 100)
    return '%s.%s' % (intcomma(int(major)), '{:.2f}'.format(minor)[2:])

@register.filter(is_safe=True)
def sb_trans(obj, field):
    return obj.get_trans(field)
