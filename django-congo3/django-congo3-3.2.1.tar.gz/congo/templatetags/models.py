# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models.base import Model
from django.db.models.fields import FieldDoesNotExist
from django.template import Library
from django.utils.translation import gettext_lazy as _

register = Library()


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
    if isinstance(model, str) or not issubclass(model, Model):
        try:
            model = apps.get_model(*model.split('.', 1))
        except LookupError:
            return _("(Brak)")

    try:
        return model._meta.get_field(field).verbose_name
    except (FieldDoesNotExist, AttributeError):
        return field.title()
