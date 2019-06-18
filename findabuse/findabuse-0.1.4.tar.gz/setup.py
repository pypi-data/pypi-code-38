# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['findabuse']

package_data = \
{'': ['*']}

install_requires = \
['bottle>=0.12.16,<0.13.0',
 'dnslib>=0.9.10,<0.10.0',
 'redis>=3.2,<4.0',
 'requests>=2.22,<3.0',
 'tornado>=6.0,<7.0']

entry_points = \
{'console_scripts': ['findabuse = findabuse.cli:main',
                     'findabusedns = findabuse.dns:main',
                     'findabusehttp = findabuse.http:main']}

setup_kwargs = {
    'name': 'findabuse',
    'version': '0.1.4',
    'description': 'findabuse.email is a simple API for looking up abuse contacts for network spaces',
    'long_description': None,
    'author': 'Matthew Gall',
    'author_email': 'git@matthewgall.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
