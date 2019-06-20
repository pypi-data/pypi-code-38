from django import template
from django.conf import settings

register = template.Library()

debconf = {
    'LOCAL_CURRENCY': settings.DEBCONF_LOCAL_CURRENCY,
}

@register.simple_tag
def debconf_setting(key):
    return debconf[key]
