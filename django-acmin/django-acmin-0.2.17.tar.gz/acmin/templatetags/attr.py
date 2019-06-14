from django import template

register = template.Library()


@register.filter
def attr(value, attr_name):
    from acmin.utils import attr
    return attr(value, attr_name, default="")
