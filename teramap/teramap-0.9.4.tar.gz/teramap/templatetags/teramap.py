import json

from django import template
from django.templatetags.static import static

from .. import __version__
from ..formatters import format_point

register = template.Library()


STATIC_FILE_FMT = "{}?version={}"


@register.simple_tag
def teramap_version():
    return __version__


@register.simple_tag
def teramap_js():
    return STATIC_FILE_FMT.format(static("teramap/teramap.js"), __version__)


@register.simple_tag
def teramap_css():
    return STATIC_FILE_FMT.format(static("teramap/teramap.css"), __version__)


@register.filter
def driving_directions(point):
    """
    Output a link with directions to point

    Use links to apple maps because it will redirect to native apps on Linux/Android and Windows.
    """
    return "https://maps.apple.com/?daddr={point.y},{point.x}".format(point=point)


register.filter(format_point)


@register.filter
def pretty_geojson(value):
    return json.dumps(value.to_geojson(), indent=4)
