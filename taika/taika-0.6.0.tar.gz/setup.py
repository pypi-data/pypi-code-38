# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['taika', 'taika.ext']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4', 'docutils', 'jinja2', 'ruamel.yaml']

entry_points = \
{'console_scripts': ['taika = taika.cli:main']}

setup_kwargs = {
    'name': 'taika',
    'version': '0.6.0',
    'description': 'Another Static Site Generator',
    'long_description': 'Taika\n=====\n\n.. image:: https://img.shields.io/pypi/v/taika.svg\n    :target: https://pypi.python.org/pypi/taika\n\n.. image:: https://readthedocs.org/projects/taika/badge/?version=latest\n    :target: https://taika.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://gitlab.com/hectormartinez/taika/badges/master/pipeline.svg\n    :target: https://gitlab.com/hectormartinez/taika/commits/master\n    :alt: Pipeline Status\n\n.. image:: https://gitlab.com/hectormartinez/taika/badges/master/coverage.svg\n    :target: https://gitlab.com/hectormartinez/taika/commits/master\n    :alt: Coverage Report\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/ambv/black\n   :alt: Code style: black\n\n\nTaika in another Static Site Generator which I created as a learning activity.\nToday I use it to build my personal page.\n\nFeatures\n--------\n\n* YAML configuration\n* Jinja2 templates\n\nLicense\n-------\n\n`MIT <./LICENSE>`__\n\n',
    'author': 'Hector Martinez',
    'author_email': 'hector.martinez.ub@gmail.com',
    'url': 'https://gitlab.com/hectormartinez/taika',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
