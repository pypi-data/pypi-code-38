# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reflected_cdn_client']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'reflected-cdn-client',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Jared Lunde',
    'author_email': 'jared.lunde@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
