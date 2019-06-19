from django import template
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


@register.inclusion_tag('leaflet-gpx/css.html')
def leaflet_gpx_css():
    return {}


@register.inclusion_tag('leaflet-gpx/js.html')
def leaflet_gpx_js():
    return {}


@register.inclusion_tag('leaflet-gpx/map-simple.html', takes_context=True)
def simple_map(context):
    return {
        'map_id': _get_map_id(),
        'map_options': json.dumps(context.get('map_options', otherwise='{}'), cls=MyJSONEncoder),
        'map_markers': json.dumps(context.get('map_markers', otherwise='[]'), cls=MyJSONEncoder),
    }


@register.inclusion_tag('leaflet-gpx/map-gpx.html', takes_context=True)
def gpx_map(context, gpx_url):
    return {
        'map_id': _get_map_id(),
        'map_options': json.dumps(context.get('map_options', otherwise='{}'), cls=MyJSONEncoder),
        'map_markers': json.dumps(context.get('map_markers', otherwise='[]'), cls=MyJSONEncoder),
        'gpx_url': gpx_url
    }
