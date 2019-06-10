# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ergal']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.21,<3.0', 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'ergal',
    'version': '1.1.1',
    'description': 'The Elegant and Readable General API Library',
    'long_description': None,
    'author': 'Elliott Maguire',
    'author_email': 'me@elliott-m.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
