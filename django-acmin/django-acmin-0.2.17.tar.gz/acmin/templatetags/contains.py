from django import template

register = template.Library()


@register.filter
def contains(value, part):
    return part in value
