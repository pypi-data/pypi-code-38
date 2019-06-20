# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['impipes']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.1,<4.0',
 'numpy>=1.16,<2.0',
 'opencv-python>=4.1,<5.0',
 'scipy>=1.3,<2.0',
 'wget>=3.2,<4.0']

setup_kwargs = {
    'name': 'impipes',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Rodolfo Ferro',
    'author_email': 'rodolfoferroperez@gmail.com',
    'url': 'https://github.com/RodolfoFerro/impipes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
