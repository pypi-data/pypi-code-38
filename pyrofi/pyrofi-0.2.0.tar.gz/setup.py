# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyrofi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyrofi',
    'version': '0.2.0',
    'description': 'Rofi Menu wrapper for hierarchical menu creation.',
    'long_description': "### About\n\nPyRofi wraps [Rofi](https://github.com/davatorium/rofi) and helps you to build the hierarchical menus with neat navigation.\n\n### Installation\n\nJust `python3 -m pip install --update --user pyrofi` (requires Python `^3.6`).\n\n### Example\n\n```python\n#!/usr/bin/env python3\n\nfrom pyrofi import run_menu\n\ndef hello_world(_):\n    print('Hello World!')\n\ndef dice():\n    import random\n    return ['echo', random.choice('123456')]\n\nrun_menu({\n    'Calculator': ['xcalc'],\n    'Games': {\n        'Rogue': ['rogue'],\n        'Angband': ['angband']\n    },\n    'Calendar': ['ncal', '2019'],\n    'Hello World': hello_world,\n    'Dice': dice,\n})\n```\n\nMore complex example you can see [here](https://github.com/astynax/pyrofi/blob/master/pyrofi/__main__.py) and run it with `python3 -m pyrofi`.\n",
    'author': 'Aleksei Pirogov',
    'author_email': 'astynax@users.noreply.github.com',
    'url': 'https://github.com/astynax/pyrofi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
