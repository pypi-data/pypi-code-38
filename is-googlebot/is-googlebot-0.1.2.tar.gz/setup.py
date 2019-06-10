# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['is_googlebot']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['tests = tests:main']}

setup_kwargs = {
    'name': 'is-googlebot',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Jared Lunde',
    'author_email': 'jared.lunde@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
