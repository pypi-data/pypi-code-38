# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_leaflet_gpx',
 'django_leaflet_gpx.migrations',
 'django_leaflet_gpx.templatetags']

package_data = \
{'': ['*'],
 'django_leaflet_gpx': ['static/leaflet-gpx/css/*',
                        'static/leaflet-gpx/js/*',
                        'templates/leaflet-gpx/*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-leaflet-gpx',
    'version': '0.1.0',
    'description': 'Simple Django application to include LeafletJS map and display GPX file',
    'long_description': 'Simple Django application to include LeafletJS map and display GPX file\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-leaflet-gpx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
