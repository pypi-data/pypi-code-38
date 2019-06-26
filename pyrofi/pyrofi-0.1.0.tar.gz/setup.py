# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyrofi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyrofi',
    'version': '0.1.0',
    'description': 'Rofi Menu wrapper for hierarchical menu creation.',
    'long_description': "### About\n\nPyRofi wraps [Rofi](https://github.com/davatorium/rofi) and helps you to build the hierarchical menus with neat navigation.\n\n### Installation\n\nJust `python3 -m pip install --user pyrofi`.\n\n### Example\n\n```python\n#!/usr/bin/env python3\n\nfrom pyrofi import run\n\nrun({\n    'Calculator': ['xcalc'],\n    'Games': {\n        'Rogue': ['rogue'],\n        'Angband': ['angband']\n    },\n    'Calendar': ['ncal', '2019']\n})\n```\n\n(You can run a similar example with `python -m pyrofi.menu`).\n",
    'author': 'Aleksei Pirogov',
    'author_email': 'astynax@users.noreply.github.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
