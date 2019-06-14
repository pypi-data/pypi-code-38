# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dfa']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'funcy>=1.12,<2.0']

setup_kwargs = {
    'name': 'dfa',
    'version': '0.1.4',
    'description': 'Python library for modeling DFAs.',
    'long_description': None,
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'marcell.vc@eecs.berkeley.edu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
