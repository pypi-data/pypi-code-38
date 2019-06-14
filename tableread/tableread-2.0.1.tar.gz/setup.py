# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tableread']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=16.0.0']

setup_kwargs = {
    'name': 'tableread',
    'version': '2.0.1',
    'description': 'Table reader for simple reStructuredText tables',
    'long_description': None,
    'author': 'Brad Brown',
    'author_email': 'brad@bradsbrown.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
