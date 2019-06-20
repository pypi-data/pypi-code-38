# -*- coding: utf-8 -*-
from congo.templatetags import common
from django.template import Library

register = Library()

@register.simple_tag
def google_maps(mode, **kwargs):
    """
    Tag zwraca mapkę google maps.
    
    {% google_maps mode="street_view" %}
    {% google_maps mode="street_view_img" %}
    {% google_maps mode="directions" %}
    {% google_maps mode="place" %}
    {% google_maps mode="place_img" %}
    {% google_maps mode="external" %}
    {% google_maps mode="external-directions" %}
    """

    return common.google_maps(mode, **kwargs)
