import types
from datetime import datetime, date

from django.utils import formats
from django.utils.timezone import localtime
from django.conf import settings

def formatDate(dt):
    if dt is None:
        return 'n.d.'
    return formats.date_format(dt, "SHORT_DATE_FORMAT")

def formatDateTime(dt):
    if dt is None:
        return 'n.d.'
    if settings.USE_TZ:
        dt = localtime(dt)
    return formats.date_format(dt, "SHORT_DATETIME_FORMAT")

def fieldlabel(obj, key):
    try:
        return obj._meta.get_field(key).verbose_name.strip() # strip serve per forzare l'esecuzione di ugettext_lazy
    except:
        model = type(obj)
        attr = getattr(model, key, None)
        if attr and hasattr(attr, "short_description"):
            return attr.short_description
        attr = getattr(obj, '%s_label' % key, None)
        if callable(attr):
            return attr()
        return key.capitalize().replace('_', ' ')

def fieldvalue(obj, key):
    try:
        return getattr(obj, 'get_%s_display' % key)()
    except:
        try:
            ret = getattr(obj, key)
        except:
            ret = None
        if type(ret) == types.MethodType:
            ret = ret()
        if ret is None:
            ret = ''
        elif isinstance(ret, datetime):
            ret = formatDateTime(ret)
        elif isinstance(ret, date):
            ret = formatDate(ret)
        return ret
