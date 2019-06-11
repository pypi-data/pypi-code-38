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
    'version': '1.6.1',
    'description': 'A flexible, powerfull and simple event trigger',
    'long_description': 'eeve\n====\n\n.. image:: https://img.shields.io/pypi/v/eeve.svg\n    :target: https://pypi.python.org/pypi/eeve\n    :alt: Latest PyPI version\n\n.. image::  https://travis-ci.org/vMarcelino/eeve.svg?branch=master\n   :target:  https://travis-ci.org/vMarcelino/eeve\n   :alt: Latest Travis CI build status\n\nA simple, flexible and powerfull event trigger\n\nUsage\n-----\n:code:`python -m eeve`\n\nOr from the project folder:\n\n:code:`python run.py`\n\nInstallation\n------------\nFrom pip:\n\n:code:`pip install -U eeve`\n\nFrom source:\n\n:code:`pip install -e .` or :code:`python setup.py install`\n\nRequirements\n^^^^^^^^^^^^\n\nCompatibility\n-------------\n\nOnly tested on windows x64, but should work on any other OS just fine. Actions and triggers, however, have their own compatibility\n\n\nLicence\n-------\nMIT Licence\n\nAuthors\n-------\n\n`eeve` was written by `Victor Marcelino <victor.fmarcelino@gmail.com>`_.\n',
    'author': 'Victor Marcelino',
    'author_email': 'victor.fmarcelino@gmail.com',
    'url': 'https://github.com/vMarcelino/eeve',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
