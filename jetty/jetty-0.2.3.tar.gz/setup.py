# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jetty', 'jetty.cli', 'jetty.util']

package_data = \
{'': ['*'], 'jetty': ['schemas/*']}

install_requires = \
['cleo>=0.6.7,<0.7.0', 'poetry>=0.12.11,<0.13.0', 'tomlkit>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['jetty = jetty.cli:run']}

setup_kwargs = {
    'name': 'jetty',
    'version': '0.2.3',
    'description': '',
    'long_description': None,
    'author': 'Andrew Halberstadt',
    'author_email': 'ahal@pm.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
