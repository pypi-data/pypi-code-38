# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nestargs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nestargs',
    'version': '0.2.1',
    'description': 'Nested arguments parser',
    'long_description': "# nestargs\n\nnestargs is a Python library that defines nested program arguments. It is based on argparse.\n\n[![PyPI](https://img.shields.io/pypi/v/nestargs.svg)](https://pypi.org/project/nestargs/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nestargs.svg)](https://pypi.org/project/nestargs/)\n[![Build Status](https://travis-ci.com/speg03/nestargs.svg?branch=master)](https://travis-ci.com/speg03/nestargs)\n[![codecov](https://codecov.io/gh/speg03/nestargs/branch/master/graph/badge.svg)](https://codecov.io/gh/speg03/nestargs)\n\nRead this in Japanese: [日本語](README.ja.md)\n\n## Installation\n\n```\npip install nestargs\n```\n\n## Usage\n\n### Basic\n\nDefine program arguments in the same way as argparse. A nested structure can be represented by putting a dot in the program argument name.\n\n```python\nimport nestargs\n\nparser = nestargs.NestedArgumentParser()\n\nparser.add_argument('--apple.n', type=int)\nparser.add_argument('--apple.price', type=float)\n\nparser.add_argument('--banana.n', type=int)\nparser.add_argument('--banana.price', type=float)\n\nargs = parser.parse_args('--apple.n=2 --apple.price=1.5 --banana.n=3 --banana.price=3.5'.split())\n# NestedNamespace(apple=NestedNamespace(n=2, price=1.5), banana=NestedNamespace(n=3, price=3.5))\n```\n\nLet's take out only the program argument apple.\n\n```python\nargs.apple\n# NestedNamespace(n=2, price=1.5)\n```\n\nYou can also get each value.\n\n```python\nargs.apple.price\n# 1.5\n```\n\nIf you want a dictionary format, you can get it this way.\n\n```python\nvars(args.apple)\n# {'n': 2, 'price': 1.5}\n```\n",
    'author': 'Takahiro Yano',
    'author_email': 'speg03@gmail.com',
    'url': 'https://github.com/speg03/nestargs',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
