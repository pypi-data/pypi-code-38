# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tildee']

package_data = \
{'': ['*']}

install_requires = \
['cssselect>=1.0,<2.0', 'lxml>=4.3,<5.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'tildee',
    'version': '0.1.0',
    'description': 'A client for tildes.net',
    'long_description': None,
    'author': 'deing',
    'author_email': 'admin@15318.de',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
