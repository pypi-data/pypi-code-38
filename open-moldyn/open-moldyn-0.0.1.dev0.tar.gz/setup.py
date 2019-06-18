# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['moldyn', 'moldyn.processing', 'moldyn.simulation', 'moldyn.utils']

package_data = \
{'': ['*'],
 'moldyn': ['data/*', 'ui/*', 'ui/qt/*'],
 'moldyn.simulation': ['templates/*']}

install_requires = \
['PyQt5>=5.12,<6.0',
 'datreant>=1.0,<2.0',
 'matplotlib>=3.1,<4.0',
 'moderngl>=5.5,<6.0',
 'numexpr>=2.6,<3.0',
 'numpy>=1.16,<2.0',
 'scipy>=1.3,<2.0']

setup_kwargs = {
    'name': 'open-moldyn',
    'version': '0.0.1.dev0',
    'description': 'Tools for molecular dynamics simulation and analysis',
    'long_description': None,
    'author': 'Arthur Luciani, Alexandre Faye-Bedrin',
    'author_email': None,
    'url': 'https://github.com/open-moldyn/moldyn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
