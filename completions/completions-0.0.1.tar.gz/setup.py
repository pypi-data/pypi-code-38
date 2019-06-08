# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['completions']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['completions = completions:main']}

setup_kwargs = {
    'name': 'completions',
    'version': '0.0.1',
    'description': 'Completion generator for shells.',
    'long_description': '# completions\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/completions',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
