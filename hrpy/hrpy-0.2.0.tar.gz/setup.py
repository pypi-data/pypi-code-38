# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hrpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hrpy',
    'version': '0.2.0',
    'description': 'hr but written in python',
    'long_description': None,
    'author': 'John Naylor',
    'author_email': 'jonaylor89@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
