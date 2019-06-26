# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['download_and_extract']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'download-and-extract',
    'version': '0.2.0',
    'description': 'Downloads zip archive and extracts it to specified folder',
    'long_description': None,
    'author': 'Advaita Krishna das',
    'author_email': 'advaita.krishna.das@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
