from django import template

register = template.Library()


@register.filter
def endswith(value, part):
    return value.endswith(part)
