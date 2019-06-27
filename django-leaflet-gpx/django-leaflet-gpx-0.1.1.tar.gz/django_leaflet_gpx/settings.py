from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static


def _get_icons():
    icons = getattr(settings, 'LEAFLET_GPX_ICONS', dict())

    if not isinstance(icons, dict):
        raise ImproperlyConfigured('LEAFLET_GPX_ICONS must be a dictionary.')

    for icon_name in icons.keys():
        if not isinstance(icons[icon_name], dict):
            raise ImproperlyConfigured('LEAFLET_GPX_ICONS["{}"] must be a dictionary.'.format(icon_name))

    if 'startIcon' not in icons:
        icons['startIcon'] = {
            'iconUrl': static('leaflet-gpx/icons/start.png'),
            'iconSize': [32, 32],
            'iconAnchor': [5, 31],
        }

    if 'endIcon' not in icons:
        icons['endIcon'] = {
            'iconUrl': static('leaflet-gpx/icons/finish.png'),
            'iconSize': [32, 32],
            'iconAnchor': [5, 31],
        }

    if 'markerIcon' not in icons:
        icons['markerIcon'] = {
            'iconUrl': static('leaflet-gpx/icons/marker.png'),
            'iconSize': [32, 32],
            'iconAnchor': [5, 31],
        }

    return icons


LEAFLET_GPX_ICONS = _get_icons()

