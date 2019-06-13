# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gluejobutils']

package_data = \
{'': ['*'], 'gluejobutils': ['.ipynb_checkpoints/*', 'data/*']}

setup_kwargs = {
    'name': 'gluejobutils',
    'version': '1.0.4',
    'description': 'Python 2.7 utils for glue jobs',
    'long_description': '# gluejobutils\nPython 2.7 utility functions to include with AWS glue jobs\n',
    'author': 'Robin Linacre',
    'author_email': 'robinlinacre@hotmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
