# -*- coding: utf-8 -*-

from django import forms
from django import template
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms.utils import ErrorDict
from django.utils.safestring import mark_safe

from common import empresa as emp

register = template.Library()


@register.filter
def nice_errors(form, non_field_msg='Erro no form'):
    """
    {% with form|nice_errors as qq %}
    """
    nice_errors = ErrorDict()
    if isinstance(form, list):
        frms = [f for f in form]
    else:
        frms = [form]

    for f in frms:
        if isinstance(f, forms.BaseForm):
            for field, errors in f.errors.items():
                if field == NON_FIELD_ERRORS:
                    key = non_field_msg
                else:
                    key = f.fields[field].label
                nice_errors[key] = errors
        if isinstance(f, forms.formsets.BaseFormSet):
            for err in f.errors:
                if err:
                    for field, errors in dict(err).items():
                        if field == NON_FIELD_ERRORS:
                            key = non_field_msg
                        else:
                            key = f.form.base_fields[field].label
                        nice_errors[key] = errors
    return nice_errors


@register.filter
def verbose_name_formset(value):
    """ {{ formset|verbose_name }} - usado em título do botão Adicionar no Detail do Master/Detail"""
    if hasattr(value, 'model'):
        return value.model._meta.verbose_name
    if hasattr(value, '_meta'):
        return value._meta.model._meta.verbose_name
    return value.Meta.model._meta.verbose_name


@register.filter
def verbose_name(value):
    """ {{ object|verbose_name }} """
    return value._meta.verbose_name


@register.filter
def verbose_name_plural(value):
    """ {{ object|verbose_name_plural }} """
    return value._meta.verbose_name_plural


# @register.filter
@register.simple_tag(takes_context=True)
def teste(context):
    """ {% if field|notprefix %} - usado em título de formset para não aparecer em empty_form """
    # a = vars(value)
    asdasd
    return a


@register.filter
def formset_id(value):
    """ {% if formsetfield|formset_id %} - usado em FormsetField para deixa o id do campo principal do formset """
    field = '%s-formset-id' % value.prefix
    return mark_safe('<input id="id_%s" name="%s" value="%s" type="hidden">' % (field, field, value.instance.pk))


@register.filter
def polymorphic_formset_id(value, formset=None):
    """ {% if formsetfield|polymorphic_formset_id %} - usado em PolymorphicFormsetField
        para deixar o id do campo principal do formset """
    # field = '%s-polymorphic-formset-id' % value.instance.__class__.__name__.lower()
    if type(formset) == dict:
        formset = formset['formset']
    field = '%s-polymorphic-formset-id' % formset.prefix
    id = value.instance.pk
    # cls = value.instance.__class__.__name__
    # value.instance.fianca._meta.related_objects[0].name
    return mark_safe('<input id="id_%s" name="%s" value="%s" type="hidden">' % (field, field, id))


@register.filter
def blank_tag(value):
    """ Remove a saída de uma variável num template.
        Usado na remoção de form.media.cs e form.media.js dos templates Ajax """
    return ''


@register.simple_tag
def empresa():
    """
    Retorna empresa.apelido
    """
    return emp.apelido


@register.filter
def get_type(value):
    return type(value)
