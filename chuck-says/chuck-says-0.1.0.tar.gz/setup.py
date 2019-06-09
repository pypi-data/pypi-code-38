# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['chuck_says']

package_data = \
{'': ['*'], 'chuck_says': ['assets/*']}

install_requires = \
['requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['chuck = chuck_says.cli:main']}

setup_kwargs = {
    'name': 'chuck-says',
    'version': '0.1.0',
    'description': 'Cowsay Chuck Norris Facts',
    'long_description': None,
    'author': 'Franccesco Orozco',
    'author_email': 'franccesco@codingdose.info',
    'url': 'https://franccesco.github.io/chuck-says',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
