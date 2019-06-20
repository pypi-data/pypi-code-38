# -*- coding: utf-8 -*-
from django.template import Library

register = Library()

@register.simple_tag(takes_context = True)
def is_active(context, active, **kwargs):
    """
    Zwraca result (domyślnie 'active'), jeśli argument active jest tożsamy z meta.active.
    
    {% is_active "home" %} zwróci 'active', jeśli do kontekstu zostanie przekazane meta = MetaData(active = "home"), lub pusty str w innym przypadku.
    {% is_active "home" result="xyz" %} zwróci 'xyz', jeśli do kontekstu zostanie przekazane meta = MetaData(active = "home"), lub pusty str w innym przypadku.
    {% is_active "home" result="bool" %} zwróci True, jeśli do kontekstu zostanie przekazane meta = MetaData(active = "home"), lub False w innym przypadku.
    """

    meta = context.get('meta', None)
    result = kwargs.get('result', 'active')

    if meta:
        if result == 'bool':
            return meta.is_active(active)
        elif meta.is_active(active):
            return result

    return ""

