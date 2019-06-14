from django import template

register = template.Library()


@register.filter
def display(obj, attr_name):
    from acmin.utils import display
    return display(obj, attr_name)
