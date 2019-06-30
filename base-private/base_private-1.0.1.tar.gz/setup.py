# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['base_private']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'base-private',
    'version': '1.0.1',
    'description': 'Encode arbitrary bits in private-use codepoints.',
    'long_description': None,
    'author': 'Morgan Wahl',
    'author_email': 'morgan.wahl@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4',
}


setup(**setup_kwargs)
