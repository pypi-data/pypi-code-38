# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['checkstat']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'colorama>=0.4.1,<0.5.0', 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['checkstat = checkstat.cli:main']}

setup_kwargs = {
    'name': 'checkstat',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Franccesco Orozco',
    'author_email': 'franccesco@codingdose.info',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
