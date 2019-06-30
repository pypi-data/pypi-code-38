# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['keylocker']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=2.7,<3.0', 'fire>=0.1.3,<0.2.0', 'pickleDB>=0.9.2,<0.10.0']

entry_points = \
{'console_scripts': ['APPLICATION-NAME = keylocker']}

setup_kwargs = {
    'name': 'keylocker',
    'version': '0.1.2',
    'description': 'Library with the CLI to save the encrypted secrets in the configuration file, but a transparent read and write the new settings in the app.',
    'long_description': None,
    'author': 'vpuhoff',
    'author_email': 'vpuhoff@live.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
