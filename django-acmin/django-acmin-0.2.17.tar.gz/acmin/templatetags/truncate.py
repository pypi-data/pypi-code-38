from django import template

register = template.Library()


@register.filter
def truncate(value, length=40):
    if value is not None and isinstance(value, str):
        if len(value) > length:
            return value[:length] + " ..."
    return value

# register.filter('truncate', truncate)
