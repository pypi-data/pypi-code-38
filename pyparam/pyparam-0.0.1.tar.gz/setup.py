# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['param']
install_requires = \
['colorama>=0.4.1,<0.5.0', 'python-simpleconf>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'pyparam',
    'version': '0.0.1',
    'description': 'Powerful parameter processing.',
    'long_description': '# pyparam\nPowerful parameter processing\n\n## Installation\n`pip install pyparam`',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
