# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['klak']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['klak = klak.cli:main']}

setup_kwargs = {
    'name': 'klak',
    'version': '0.4.0',
    'description': 'Klak provides the ergonoics of a project Makefile with the ease of Python and power of Click.',
    'long_description': None,
    'author': 'Aubrey Taylor',
    'author_email': 'aubricus+klak@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
