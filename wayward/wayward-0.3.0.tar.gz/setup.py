# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['wayward']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0']

setup_kwargs = {
    'name': 'wayward',
    'version': '0.3.0',
    'description': 'Wayward is a Python package that helps to identify characteristic terms from single documents or groups of documents.',
    'long_description': None,
    'author': 'Alex Olieman',
    'author_email': 'alex@olieman.net',
    'url': 'https://github.com/aolieman/weighwords',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
