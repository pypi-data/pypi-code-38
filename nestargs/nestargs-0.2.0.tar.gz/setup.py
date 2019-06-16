# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nestargs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nestargs',
    'version': '0.2.0',
    'description': 'Nested arguments parser',
    'long_description': '# nestargs\n\nNested arguments parser\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nestargs.svg)](https://pypi.org/project/nestargs/)\n[![Build Status](https://travis-ci.com/speg03/nestargs.svg?branch=master)](https://travis-ci.com/speg03/nestargs)\n[![codecov](https://codecov.io/gh/speg03/nestargs/branch/master/graph/badge.svg)](https://codecov.io/gh/speg03/nestargs)\n',
    'author': 'Takahiro Yano',
    'author_email': 'speg03@gmail.com',
    'url': 'https://github.com/speg03/nestargs',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
