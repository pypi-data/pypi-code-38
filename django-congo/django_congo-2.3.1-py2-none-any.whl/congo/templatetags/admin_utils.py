# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models.fields import FieldDoesNotExist
from django.template import Library

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

@register.filter
def content_type_id(value):
    """
    Tag zwraca content_type__id dla podanego obiektu.
    {% content_type_id obj %}
    """

    try:
        content_type = ContentType.objects.get_for_model(value)
        return content_type.id
    except AttributeError:
        return None

@register.filter
def class_name(obj):
    """
    Tag zwraca nazwe klasy podanego obiektu.
    """

    return obj.__class__.__name__

@register.filter
def module_class_name(obj):
    """
    Tag zwraca ścieżke modułu dla podanego obiektu. Np. accounts.AbstractUser
    """
    return "%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)

@register.filter
def field_name(model, field):
    try:
        return model._meta.get_field(field).verbose_name
    except (FieldDoesNotExist, AttributeError):
        return field.title()
