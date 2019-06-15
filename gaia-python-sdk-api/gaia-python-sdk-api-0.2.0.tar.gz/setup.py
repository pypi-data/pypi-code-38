# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gaia_python_sdk_api']

package_data = \
{'': ['*'], 'gaia_python_sdk_api': ['transporter/*']}

setup_kwargs = {
    'name': 'gaia-python-sdk-api',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Leftshift One',
    'author_email': 'contact@leftshift.one',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
