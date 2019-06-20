# -*- coding: utf-8 -*-
from django.template import Library
from django.urls import reverse, NoReverseMatch

register = Library()

@register.filter
def admin_change_url(value):
    """
    Tag zwraca url'a do change_view w adminie dla podanego obiektu.
    
    {% admin_change_url obj %}
    
    Odpowiednik:
    {% url 'admin:index' %}
    {% url 'admin:polls_choice_add' %}
    {% url 'admin:polls_choice_change' choice.id %}
    {% url 'admin:polls_choice_changelist' %}
    """

    url = ""
    try:
        url = reverse('admin:%s_%s_change' % (value._meta.app_label, value._meta.model_name), args = (value.id,))
    except (NoReverseMatch, AttributeError):
        pass
    return url
