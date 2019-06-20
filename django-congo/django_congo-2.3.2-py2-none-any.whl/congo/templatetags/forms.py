# -*- coding: utf-8 -*-
from django.template import Library
from django import forms

register = Library()

@register.filter
def field_type(field):
    return field.field.widget.__class__.__name__

@register.filter
def is_field_type(field, val):
    return field.field.widget.__class__.__name__ == val

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.widgets.CheckboxInput)

@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.widgets.Select)

@register.filter
def is_radio_choice(field):
    return isinstance(field.field.widget, forms.widgets.RadioChoiceInput)

@register.filter
def is_checkbox_choice(field):
    return isinstance(field.field.widget, forms.widgets.CheckboxChoiceInput)

@register.filter
def is_hidden(field):
    return isinstance(field.field.widget, forms.widgets.HiddenInput)
