# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['brew_tools']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['brew_tools = brew_tools.command_line:run']}

setup_kwargs = {
    'name': 'brew-tools',
    'version': '0.2.2',
    'description': '',
    'long_description': '',
    'author': 'Sven',
    'author_email': 'sven@unlogic.co.uk',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
