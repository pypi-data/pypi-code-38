# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cliar']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cliar',
    'version': '1.2.4',
    'description': 'Create CLIs with classes and type hints.',
    'long_description': "[![image](https://img.shields.io/pypi/v/cliar.svg)](https://pypi.org/project/cliar)\n[![image](https://travis-ci.org/moigagoo/cliar.svg?branch=develop)](https://travis-ci.org/moigagoo/cliar)\n[![image](https://codecov.io/gh/moigagoo/cliar/branch/develop/graph/badge.svg)](https://codecov.io/gh/moigagoo/cliar)\n\n# Cliar\n\n**Cliar** is yet another Python package to help you create commandline interfaces. It focuses on simplicity and extensibility:\n\n-   Creating a CLI is as simple as subclassing a Python class from `cliar.Cliar`.\n-   Extending a CLI is as simple as extending the class with inheritance.\n\nCliar's mission is to let you focus on the business logic instead of building an interface for it. At the same time, Cliar doesn't want to stand in your way, so it provides the means to customize the generated CLI.\n\n\n## Installation\n\n```shell\n$ pip install cliar\n```\n\nCliar requires Python 3.6+ and was tested on Windows, Linux, and macOS. There are no dependencies outside Python's standard library.\n\n\n## Basic Usage\n\nLet's create a commandline calculator that adds two real numbers:\n\n```python\nfrom cliar import Cliar\n\n\nclass Calculator(Cliar):\n'''Calculator app.'''\n\n    def add(self, x: float, y: float):\n    '''Add two real numbers.'''\n\n        print(f'The sum of {x} and {y} is {x+y}.')\n\n\nif __name__ == '__main__':\n    Calculator().parse()\n```\n\nSave this code to `calc.py` and run it with different inputs:\n\n-   Valid input:\n\n        $ python calc.py add 12 34\n        The sum of 12.0 and 34.0 is 46.0.\n\n-   Invalid input:\n\n        $ python calc.py add foo bar\n        usage: calc.py add [-h] x y\n        calc.py add: error: argument x: invalid float value: 'foo'\n\n-   Get help:\n\n        $ python calc.py -h\n        usage: calc.py [-h] {add} ...\n\n        Calculator app.\n\n        optional arguments:\n        -h, --help  show this help message and exit\n\n        commands:\n        {add}       Available commands:\n            add       Add two real numbers.\n\n-   Get help for a specific command:\n\n        $ python calc.py add -h\n        usage: calc.py add [-h] x y\n\n        Add two real numbers.\n\n        positional arguments:\n        x\n        y\n\n        optional arguments:\n        -h, --help  show this help message and exit\n\nThere are a few things to note here:\n\n-   It's a regular Python class with a regular Python method. You don't need to learn any new syntax to use Cliar.\n\n-   The `add` method is converted into `add` command, and its positional params are converted into positional commandline args.\n\n-   We don't convert `x` or `y` to `float` or handle any potential conversion errors in the `add` body. Instead, we treat `x` and `y` as if they were already guaranteed to be floats. That's because Cliar does the validation and conversion for us, using the information from `add`'s type hints. Note how invalid input doesn't even reach your code.\n\n-   The `--help` and `-h` flags are added automatically and the help messages are generated from the docstrings.\n\n\n## Read Next\n\n-   [Tutorial →](https://moigagoo.github.io/cliar/tutorial/)\n-   [Cliar vs. Click vs. docopt →](https://moigagoo.github.io/cliar/comparison/)\n",
    'author': 'Konstantin Molchanov',
    'author_email': 'moigagoo@live.com',
    'url': 'https://moigagoo.github.io/cliar/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
