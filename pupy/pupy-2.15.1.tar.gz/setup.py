# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pupy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pupy',
    'version': '2.15.1',
    'description': 'pretty useful python',
    'long_description': None,
    'author': 'jessekrubin',
    'author_email': 'jessekrubin@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
