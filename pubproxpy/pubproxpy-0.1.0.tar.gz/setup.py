# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pubproxpy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'pubproxpy',
    'version': '0.1.0',
    'description': 'An easy to use Python wrapper for pubproxy.com',
    'long_description': None,
    'author': 'LovecraftianHorror',
    'author_email': 'LovecraftianHorror@pm.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
