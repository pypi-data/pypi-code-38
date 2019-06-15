# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gaia_python_sdk_atlas']

package_data = \
{'': ['*']}

install_requires = \
['gaia-python-sdk-api>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'gaia-python-sdk-atlas',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Leftshift One',
    'author_email': 'contact@leftshift.one',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
