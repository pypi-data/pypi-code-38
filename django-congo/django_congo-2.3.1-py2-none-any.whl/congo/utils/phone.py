# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.defaultfilters import lower, upper
from django.utils.formats import number_format

def get_phone_number_prefixes():
    """
    Zwraca liste slownik�w prefixow numerow telefonu.
    
    Np. ``get_phone_number_prefixes()`` zwróci ``[{'code': 'pl', 'name': 'Polska', 'prefix': '48'}, ...]``
    """
    phone_prefixes = []
    for k, v in settings.CONGO_COUNTRIES:
        try:
            phone_prefixes.append({
                'code' : lower(k),
                'name' : v,
                'prefix' : settings.CONGO_PHONE_PREFIXES[k]
            })
        except KeyError:
            pass

    return phone_prefixes

def render_phone_prefix(country_code):
    """
    Renderduje prefix numeru telefonu dla kodu kraju
    
    Np. ``render_phone_prefix('pl')`` zwr�ci "+48"
    """
    return "+%s" % settings.CONGO_PHONE_PREFIXES[upper(country_code)]

def render_phone_with_prefix(country_code, phone_number):
    """
    Renderuje numer telefonu z numerem kierunkowym
  
    Np. ``render_phone_with_prefix('pl', 665121218)`` zwróci "+48665121218"
    """
    return "%s%s" % (render_phone_prefix(country_code), phone_number)
