# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['autosequence']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-autosequence',
    'version': '0.6.0',
    'description': 'A Django model field providing a configurable automatic sequence of values.',
    'long_description': None,
    'author': 'Andrew Cordery',
    'author_email': 'cordery@gmail.com',
    'url': 'https://github.com/cordery/django-autosequence',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
