# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['monobank']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'monobank',
    'version': '0.2.1',
    'description': 'Monobank.ua API implementation',
    'long_description': None,
    'author': 'Vitaliy Kucheriavyi',
    'author_email': 'ppr.vitaly@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
