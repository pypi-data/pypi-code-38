# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['terrarium',
 'terrarium._version',
 'terrarium.adapters',
 'terrarium.algorithms',
 'terrarium.builders',
 'terrarium.graphs',
 'terrarium.models',
 'terrarium.schemas',
 'terrarium.utils']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'dill>=0.2.9,<0.3.0',
 'pydent==0.1.2a',
 'termcolor>=1.1,<2.0',
 'webcolors>=1.9,<2.0']

entry_points = \
{'console_scripts': ['name = terrarium:_version.get_name',
                     'upver = terrarium:_version.pull_version',
                     'version = terrarium:_version.get_version']}

setup_kwargs = {
    'name': 'terrarium-capp',
    'version': '0.0.1a0',
    'description': 'Adaptive Computer Aided Process Planner',
    'long_description': '# Terrarium\n\n[![PyPI version](https://badge.fury.io/py/terrarium-capp.svg)](https://badge.fury.io/py/terrarium-capp)\n\n## Forward Planning Algorithm\n\nAdaptive (?) Directed Steiner Tree with Groups:\n',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/jvrana/Terrarium',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
