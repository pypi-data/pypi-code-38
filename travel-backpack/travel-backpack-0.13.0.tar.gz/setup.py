# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['travel_backpack']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'travel-backpack',
    'version': '0.13.0',
    'description': 'Some very useful functions and classes to use in day-to-day',
    'long_description': 'travel-backpack\n===============\n\n.. image:: https://img.shields.io/pypi/v/travel-backpack.svg\n    :target: https://pypi.python.org/pypi/travel-backpack\n    :alt: Latest PyPI version\n\n.. image:: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal.png\n   :target: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal\n   :alt: Latest Travis CI build status\n\nSome very useful functions and classes to use in day-to-day\n\nUsage\n-----\n\nInstallation\n------------\n\nRequirements\n^^^^^^^^^^^^\n\nCompatibility\n-------------\n\nLicence\n-------\n\nAuthors\n-------\n\n`travel-backpack` was written by `Victor Marcelino <victor.fmarcelino@gmail.com>`_.\n',
    'author': 'Victor Marcelino',
    'author_email': None,
    'url': 'https://github.com/vMarcelino/travel-backpack',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
