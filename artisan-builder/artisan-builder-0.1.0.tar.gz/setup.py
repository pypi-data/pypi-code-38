# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['artisan']

package_data = \
{'': ['*']}

install_requires = \
['cbor2', 'falcon', 'gunicorn', 'h5py', 'jsonschema', 'numpy', 'ruamel.yaml']

setup_kwargs = {
    'name': 'artisan-builder',
    'version': '0.1.0',
    'description': 'A build system for explainable science',
    'long_description': 'Artisan is a build system for explainable science. The full documentation can be\nfound `here <https://masonmcgill.github.io/artisan/>`_.\n',
    'author': 'Mason McGill',
    'author_email': 'mmcgill@caltech.edu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
