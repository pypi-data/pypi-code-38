# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['harriet']

package_data = \
{'': ['*']}

install_requires = \
['channels>=2.2,<3.0', 'django>=2.0,<3.0', 'djangorestframework>=3.9,<4.0']

setup_kwargs = {
    'name': 'harriet',
    'version': '0.1.0',
    'description': 'Integrate DRF and Channels-based websockets.',
    'long_description': '=======\nHarriet\n=======\n\n- version number: 0.1.0\n- author: Kit La Touche\n\nOverview\n--------\n\nIntegrate DRF and Channels-based websockets.\n\nInstallation / Usage\n--------------------\n\nTo install use pip::\n\n    $ pip install harriet\n\n\nOr clone the repo::\n\n    $ git clone https://github.com/wlonk/harriet.git\n    $ python setup.py install\n    \nContributing\n------------\n\nTBD\n\nExample\n-------\n\nTBD\n',
    'author': 'Kit La Touche',
    'author_email': 'kit@transneptune.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
