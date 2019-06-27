# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tabbyj']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'ujson>=1.35,<2.0']

entry_points = \
{'console_scripts': ['tabbyj = tabbyj.__main__:tabbyj']}

setup_kwargs = {
    'name': 'tabbyj',
    'version': '0.2.1',
    'description': 'A command line JSON flattener',
    'long_description': None,
    'author': 'Riley Flynn',
    'author_email': 'riley@rileyflynn.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
