# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['eeve', 'eeve.eeve actions.eeve_GUI', 'eeve.eeve plugins.win_key_hook']

package_data = \
{'': ['*'],
 'eeve': ['eeve actions/*',
          'eeve actions/eeve_GUI/Controllers/*',
          'eeve actions/eeve_GUI/Views/*',
          'eeve plugins/*',
          'eeve triggers/*']}

install_requires = \
['travel-backpack>=0.12.0']

setup_kwargs = {
    'name': 'eeve',
    'version': '1.6.0',
    'description': 'A flexible, powerfull and simple event trigger',
    'long_description': 'eeve\n====\n\n.. image:: https://img.shields.io/pypi/v/eeve.svg\n    :target: https://pypi.python.org/pypi/eeve\n    :alt: Latest PyPI version\n\n.. image::  https://travis-ci.org/vMarcelino/eeve.svg?branch=master\n   :target:  https://travis-ci.org/vMarcelino/eeve\n   :alt: Latest Travis CI build status\n\nA flexible, powerfull and simple event trigger\n\nUsage\n-----\n\nInstallation\n------------\n\nRequirements\n^^^^^^^^^^^^\n\nCompatibility\n-------------\n\nLicence\n-------\n\nAuthors\n-------\n\n`eeve` was written by `Victor Marcelino <victor.fmarcelino@gmail.com>`_.\n',
    'author': 'Victor Marcelino',
    'author_email': 'victor.fmarcelino@gmail.com',
    'url': 'https://github.com/vMarcelino/eeve',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
