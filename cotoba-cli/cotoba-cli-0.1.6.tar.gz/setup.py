# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cotoba_cli']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0',
 'click>=7.0,<8.0',
 'pytz>=2019,<2020',
 'requests>=2.21,<3.0',
 'toml>=0,<1',
 'warrant>=0,<1']

entry_points = \
{'console_scripts': ['cotoba = cotoba_cli.cli:cli_root']}

setup_kwargs = {
    'name': 'cotoba-cli',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
