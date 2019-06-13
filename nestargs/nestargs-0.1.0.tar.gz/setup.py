# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nestargs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nestargs',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Takahiro Yano',
    'author_email': 'speg03@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
