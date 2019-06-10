# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['is_googlebot']

package_data = \
{'': ['*']}

install_requires = \
['ua-parser>=0.8.0,<0.9.0', 'user_agents>=2.0,<3.0']

setup_kwargs = {
    'name': 'is-googlebot',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Jared Lunde',
    'author_email': 'jared.lunde@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
