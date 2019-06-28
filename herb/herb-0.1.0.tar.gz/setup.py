# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['herb']

package_data = \
{'': ['*']}

install_requires = \
['more_itertools>=7.1,<8.0', 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'herb',
    'version': '0.1.0',
    'description': 'Effortless Offline Backups',
    'long_description': None,
    'author': 'eukaryote',
    'author_email': 'eukaryote31@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
