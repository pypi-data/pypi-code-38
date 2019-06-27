from django import template
from django_leaflet_gpx.settings import LEAFLET_GPX_ICONS
import decimal
import json
import random
import string

register = template.Library()


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


def _get_map_id():
    return 'map-' + ''.join(random.sample(string.ascii_lowercase, 5))


def _get_default_result(context):

    options = context.get('map_options', otherwise={})
    if 'icons' not in options:
        options['icons'] = LEAFLET_GPX_ICONS
    else:
        for icon_name in LEAFLET_GPX_ICONS.keys():
            if icon_name not in options['icons']:
                options['icons'][icon_name] = LEAFLET_GPX_ICONS[icon_name]

    markers = context.get('map_markers', otherwise=[])

    return {
        'map_id': _get_map_id(),
        'map_options': json.dumps(options, cls=MyJSONEncoder),
        'map_markers': json.dumps(markers, cls=MyJSONEncoder),
    }


@register.inclusion_tag('leaflet-gpx/css.html')
def leaflet_gpx_css():
    return {}


@register.inclusion_tag('leaflet-gpx/js.html')
def leaflet_gpx_js():
    return {}


@register.inclusion_tag('leaflet-gpx/map-simple.html', takes_context=True)
def simple_map(context):
    return _get_default_result(context)


@register.inclusion_tag('leaflet-gpx/map-gpx.html', takes_context=True)
def gpx_map(context, gpx_url):
    result = _get_default_result(context)
    result['gpx_url'] = gpx_url
    return result
