# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lstar']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'dfa>=0.1.3,<0.2.0', 'funcy>=1.12,<2.0']

setup_kwargs = {
    'name': 'lstar',
    'version': '0.1.1',
    'description': 'Python implementation of lstar automata learning algorithm.',
    'long_description': None,
    'author': 'Marcell J. Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
