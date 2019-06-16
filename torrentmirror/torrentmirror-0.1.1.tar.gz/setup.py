# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['torrentmirror']

package_data = \
{'': ['*']}

install_requires = \
['delver>=0.1.6,<0.2.0',
 'docopt>=0.6.2,<0.7.0',
 'robobrowser>=0.5.3,<0.6.0',
 'tabulate>=0.8.3,<0.9.0']

entry_points = \
{'console_scripts': ['torrentmirror = torrentmirror:main']}

setup_kwargs = {
    'name': 'torrentmirror',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'David Francos',
    'author_email': 'opensource@davidfrancos.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
