from django import template

register = template.Library()


@register.filter
def concat(value, other):
    return "%s%s" % (str(value), str(other))
