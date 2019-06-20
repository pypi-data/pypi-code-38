# -*- coding: utf-8 -*-
from django import forms

def add_widget_css_class(obj, css_class, exclude_field_types = None):
    """
    Adds css class for all forms fields or one field or exclude fieldtype
    """
    exclude_field_types = [] if not exclude_field_types else exclude_field_types

    if isinstance(obj, (forms.Form, forms.ModelForm)):
        for field_name, field in obj.fields.items():
            if not field.widget.__class__.__name__ in exclude_field_types:
                add_widget_attr(obj.fields[field_name], 'class', css_class)
    else:
        add_widget_attr(obj, 'class', css_class)

def set_widget_placeholder(obj):
    """
    Sets placeholder for all forms fields or one field
    """
    if isinstance(obj, (forms.Form, forms.ModelForm)):
        for field_name in obj.fields:
            field = obj.fields[field_name]
            set_widget_attr(field, 'placeholder', field.label)
    else:
        set_widget_attr(obj, 'placeholder', obj.label)

def set_widget_ng_model(obj, prefix = 'obj'):
    """
    Sets ng-model for all forms fields or one field
    """
    if isinstance(obj, (forms.Form, forms.ModelForm)):
        for field_name in obj.fields:
            field = obj.fields[field_name]
            set_widget_attr(field, 'ng-model', '%s.%s' % (prefix, field_name))
    else:
        set_widget_attr(obj, 'ng-model', '%s.%s' % (prefix, field_name))

def add_widget_attr(field, attr, value):
    if attr in field.widget.attrs and field.widget.attrs[attr]:
        field.widget.attrs[attr] += " %s" % value
    else:
        field.widget.attrs[attr] = value

def set_widget_attr(field, attr, value):
    field.widget.attrs[attr] = value
