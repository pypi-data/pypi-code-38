# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['main_dec']

package_data = \
{'': ['*']}

install_requires = \
['docstring-parser>=0.3.0,<0.4.0', 'stringcase>=1.2,<2.0']

setup_kwargs = {
    'name': 'main-dec',
    'version': '0.1.0',
    'description': 'A tiny library for creating CLIs',
    'long_description': None,
    'author': 'Sune Debel',
    'author_email': 'sad@archii.ai',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
