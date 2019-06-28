"""
Some useful template tag examples to display forms and formsets easier.
"""
import json

from django.template import TemplateSyntaxError
from django.template.library import Library
from django.utils.encoding import force_text
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from polymorphic.formsets import BasePolymorphicModelFormSet

register = Library()


@register.filter()
def include_empty_form(formset):
    """
    Make sure the "empty form" is included when displaying a formset (typically table with input rows)
    """
    if type(formset) == dict:
        formset = formset['formset']

    for form in formset:
        yield form

    if hasattr(formset, 'empty_forms'):
        # BasePolymorphicModelFormSet from django-polymorphic 1.0b1
        for form in formset.empty_forms:
            yield form
    else:
        # Standard Django formset
        yield formset.empty_form


@register.filter()
def empty_forms(formset):
    """
    Lista somente os empty forms para os vários tipos do PolymorphicModel
    """
    if hasattr(formset, 'empty_forms'):
        # BasePolymorphicModelFormSet from django-polymorphic 1.0b1
        for form in formset.empty_forms:
            yield form
    else:
        # Standard Django formset
        yield formset.empty_form


@register.filter
def as_non_field_errors(form):
    """
    Properly format field errors if they exist.
    """
    errors = form.non_field_errors()
    if errors:
        return mark_safe('<span class="help-block"><strong>{}</strong></span>'.format('<br>'.join(map(escape, errors))))
    else:
        return ''


@register.filter
def as_non_form_errors(formset):
    """
    Properly format the formset errors.
    """
    errors = formset.non_form_errors()
    if errors:
        return format_html('<div class="has-error"><span class="help-block"><strong>{0}</strong></span></div>',
                           '<br>'.join(map(escape, errors)))
    else:
        return ''


@register.filter()
def as_field_errors(field):
    """
    Properly format field errors if they exist.
    """
    if not field:
        raise TemplateSyntaxError("Invalid field name passed to as_field_errors filter")
    if field.errors:
        return format_html('<span class="help-block"><strong>{0}</strong></span>',
                           '<br>'.join(map(escape, field.errors)))
    else:
        return ''


@register.filter
def as_script_options(formset):
    """
    A JavaScript data structure for the JavaScript code

    This generates the ``data-options`` attribute for ``jquery.django-inlines.js``
    The formset may define the following extra attributes:

    - ``verbose_name``
    - ``add_text``
    - ``show_add_button``
    """
    if type(formset) == dict:
        formset = formset['formset']
    try:
        model = formset.model
    except Exception:
        model = formset._meta.model

    verbose_name = getattr(formset, 'verbose_name', model._meta.verbose_name)

    can_add = formset.instance.can_add if hasattr(formset.instance, 'can_add') else True
    # print('as_script_options:', can_add)
    # from django.db import connection
    # print(connection.queries)

    options = {
        'prefix': formset.prefix,
        'pkFieldName': model._meta.pk.name,
        'addText': getattr(formset, 'add_text', None) or 'Adicionar {}'.format(capfirst(verbose_name)),
        'showAddButton': getattr(formset, 'show_add_button', True) and can_add,
        'deleteText': 'Excluir',
    }

    if isinstance(formset, BasePolymorphicModelFormSet):
        # Allow to add different types
        options['childTypes'] = [
            {
                'name': force_text(model._meta.verbose_name),
                'type': model._meta.model_name,
            } for model in formset.child_forms.keys()
        ]

    return json.dumps(options)


@register.filter
def as_model_name(model):
    """
    Usage: ``{{ model|as_model_name }}``
    """
    return model._meta.model_name


@register.filter
def as_form_type(form):
    """
    Usage: ``{{ form|as_form_type }}``
    """
    return form._meta.model._meta.model_name


@register.filter
def as_verbose_name(obj):
    """
    Usage: ``{{ obj|as_verbose_name }}``
    """
    return force_text(obj._meta.verbose_name)
