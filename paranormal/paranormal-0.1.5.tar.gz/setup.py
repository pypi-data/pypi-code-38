# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['paranormal']

package_data = \
{'': ['*'], 'paranormal': ['test/*']}

install_requires = \
['PyYAML>=5.1,<6.0', 'numpy>=1.16,<2.0', 'pampy>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'paranormal',
    'version': '0.1.5',
    'description': 'Coherent management of large parameter lists in Python',
    'long_description': None,
    'author': 'Schuyler Fried',
    'author_email': 'schuylerfried@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6',
}


setup(**setup_kwargs)
