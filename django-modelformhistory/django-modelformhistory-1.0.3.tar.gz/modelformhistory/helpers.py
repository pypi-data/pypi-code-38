# coding: utf-8
from __future__ import print_function, division, absolute_import, unicode_literals

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django import forms


def get_object_repr(instance):
    return "%s %s" % (type(instance)._meta.verbose_name.title(), instance)


def get_human_value_for_field(bounded_field, value):
    if value is None:
        return _("Empty")

    value = bounded_field.field.clean(value)

    if not isinstance(value, str) and hasattr(value, "__iter__"):
        # iterable
        return ", ".join([force_text(i) for i in value])

    elif isinstance(value, models.Model):
        # FK or single M2M
        return force_text(value)

    elif isinstance(bounded_field.field, (forms.MultipleChoiceField, forms.ChoiceField)):
        # choiceField
        return dict(bounded_field.field.choices).get(value)

        # TODO Boolean

    return value
