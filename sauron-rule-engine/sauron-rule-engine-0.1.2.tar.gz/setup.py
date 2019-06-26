# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sauron_rule_engine']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sauron-rule-engine',
    'version': '0.1.2',
    'description': 'A simple rule engine implemented in python',
    'long_description': None,
    'author': 'jlugao',
    'author_email': 'joaolhullier@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
