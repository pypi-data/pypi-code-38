# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cosilico_runner']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cosilico-runner = cosilico_runner:cosilico_runner.main']}

setup_kwargs = {
    'name': 'cosilico-runner',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Erik Storrs',
    'author_email': 'epstorrs@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
