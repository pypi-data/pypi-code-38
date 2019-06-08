# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['moltransform']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0']

setup_kwargs = {
    'name': 'moltransform',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Rodolfo Ferro',
    'author_email': 'rodolfoferroperez@gmail.com',
    'url': 'https://github.com/RodolfoFerro/moltransform',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
