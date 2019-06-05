# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cranial']

package_data = \
{'': ['*'], 'cranial': ['common/*']}

setup_kwargs = {
    'name': 'cranial-common',
    'version': '0.3.0',
    'description': 'Low-level utilities shared by various Cranial packages.',
    'long_description': None,
    'author': 'Matt Chapman, et al.',
    'author_email': 'Matt@NinjitsuWeb.com',
    'url': 'https://github.com/tribune/cranial-common',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
