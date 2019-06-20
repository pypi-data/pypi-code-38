from django.template import Library
from ..parse import parse_html
register = Library()


@register.filter()
def oembed(value, simplified=False):
    return parse_html(value, ajax=not simplified)
