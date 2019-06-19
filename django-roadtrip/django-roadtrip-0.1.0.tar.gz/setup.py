# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_roadtrip', 'django_roadtrip.migrations']

package_data = \
{'': ['*'],
 'django_roadtrip': ['templates/roadtrip/*', 'templates/roadtrip/partials/*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-roadtrip',
    'version': '0.1.0',
    'description': 'Django application to inform and follow your friends during road-trip',
    'long_description': 'Django application to inform and follow your friends during road trips.\n\nNot documented yet :-/\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-roadtrip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
