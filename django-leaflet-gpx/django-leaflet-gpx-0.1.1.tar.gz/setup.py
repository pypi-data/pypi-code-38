# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_leaflet_gpx',
 'django_leaflet_gpx.migrations',
 'django_leaflet_gpx.templatetags']

package_data = \
{'': ['*'],
 'django_leaflet_gpx': ['static/leaflet-gpx/css/*',
                        'static/leaflet-gpx/css/images/*',
                        'static/leaflet-gpx/icons/*',
                        'static/leaflet-gpx/js/*',
                        'templates/leaflet-gpx/*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-leaflet-gpx',
    'version': '0.1.1',
    'description': 'Simple Django application to include LeafletJS map and display GPX file',
    'long_description': "Simple Django application to include LeafletJS map and display GPX file.\n\nNot documented yet :-/\n\n\n## Configuration\n\nThis is an example of custom configuration\n\n    import os\n    \n    STATIC_URL = '/static'\n    LEAFLET_GPX_ICONS = {\n        'markerIcon': {\n            'iconUrl': os.path.join(STATIC_URL, 'icons/my-custom-marker.png'),\n            'iconSize': [32, 32],\n            'iconAnchor': [5, 31],\n        }\n    }\n\n### LEAFLET_GPX_ICONS\n\nThere are three editable icons: \n\n- **markerIcon**: markers points\n- **startIcon**: GPX start point\n- **endIcon**: GPX end point\n\nThe icon options are the same as those for creating an icon in the Leaflet-JS library.  \nHere is a link to the documentation: <https://leafletjs.com/reference-1.5.0.html#icon>\n\n",
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-leaflet-gpx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
