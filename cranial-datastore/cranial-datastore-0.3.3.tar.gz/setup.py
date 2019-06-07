# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cranial', 'cranial.connectors', 'cranial.keyvalue']

package_data = \
{'': ['*'],
 'cranial': ['.mypy_cache/*',
             '.mypy_cache/3.5/*',
             '.mypy_cache/3.5/collections/*',
             '.mypy_cache/3.5/cranial/*',
             '.mypy_cache/3.5/cranial/__init__/*',
             '.mypy_cache/3.5/cranial/connectors/*',
             '.mypy_cache/3.5/importlib/*',
             '.mypy_cache/3.5/os/*',
             'datastore/*',
             'datastore/adapters/*'],
 'cranial.connectors': ['.mypy_cache/*',
                        '.mypy_cache/3.5/*',
                        '.mypy_cache/3.5/collections/*',
                        '.mypy_cache/3.5/cranial/*',
                        '.mypy_cache/3.5/cranial/connectors/*',
                        '.mypy_cache/3.5/cranial/connectors/s3/*',
                        '.mypy_cache/3.5/importlib/*',
                        '.mypy_cache/3.5/logging/*',
                        '.mypy_cache/3.5/os/*',
                        '.mypy_cache/3.5/unittest/*']}

install_requires = \
['boto3>=1.9,<2.0', 'cachetools>=2.1,<3.0', 'cranial-common>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'cranial-datastore',
    'version': '0.3.3',
    'description': 'Data storage connectivity & utilities for Cranial.',
    'long_description': None,
    'author': 'Matt Chapman et al.',
    'author_email': 'Matt@NinjitsuWeb.com',
    'url': 'https://github.com/tribune/cranial-datastore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
