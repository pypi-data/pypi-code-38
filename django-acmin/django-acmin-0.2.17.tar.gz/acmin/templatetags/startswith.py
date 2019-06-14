from django import template

register = template.Library()


@register.filter
def startswith(value, part):
    return value.startswith(part)
