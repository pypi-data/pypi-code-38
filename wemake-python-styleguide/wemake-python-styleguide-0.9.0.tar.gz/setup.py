# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['wemake_python_styleguide',
 'wemake_python_styleguide.logics',
 'wemake_python_styleguide.logics.naming',
 'wemake_python_styleguide.options',
 'wemake_python_styleguide.presets',
 'wemake_python_styleguide.transformations',
 'wemake_python_styleguide.transformations.ast',
 'wemake_python_styleguide.violations',
 'wemake_python_styleguide.visitors',
 'wemake_python_styleguide.visitors.ast',
 'wemake_python_styleguide.visitors.ast.complexity',
 'wemake_python_styleguide.visitors.filenames',
 'wemake_python_styleguide.visitors.tokenize']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.7.1,<0.9.0',
 'attrs',
 'flake8-annotations-complexity>=0.0.1,<0.0.3',
 'flake8-bandit>=1,<3',
 'flake8-broken-line>=0.1,<0.2',
 'flake8-bugbear>=19.3,<20.0',
 'flake8-builtins>=1.4,<2.0',
 'flake8-coding>=1.3,<2.0',
 'flake8-commas>=2.0,<3.0',
 'flake8-comprehensions>=1.4,<3.0',
 'flake8-debugger>=3.1,<4.0',
 'flake8-docstrings>=1.3,<2.0',
 'flake8-eradicate>=0.2,<0.3',
 'flake8-isort>=2.6,<3.0',
 'flake8-logging-format>=0.6,<0.7',
 'flake8-pep3101>=1.2,<2.0',
 'flake8-print>=3.1,<4.0',
 'flake8-quotes>=1,<3',
 'flake8-string-format>=0.2,<0.3',
 'flake8>=3.7,<4.0',
 'pep8-naming>=0.7,<0.9',
 'typing_extensions>=3.6,<4.0']

entry_points = \
{'flake8.extension': ['Z = wemake_python_styleguide.checker:Checker']}

setup_kwargs = {
    'name': 'wemake-python-styleguide',
    'version': '0.9.0',
    'description': 'The strictest and most opinionated python linter ever',
    'long_description': '# wemake-python-styleguide\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)\n[![Python Version](https://img.shields.io/pypi/pyversions/wemake-python-styleguide.svg)](https://pypi.org/project/wemake-python-styleguide/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n[![Build Status](https://travis-ci.org/wemake-services/wemake-python-styleguide.svg?branch=master)](https://travis-ci.org/wemake-services/wemake-python-styleguide) \n[![Coverage](https://coveralls.io/repos/github/wemake-services/wemake-python-styleguide/badge.svg?branch=master)](https://coveralls.io/github/wemake-services/wemake-python-styleguide?branch=master)\n[![Documentation Status](https://readthedocs.org/projects/wemake-python-styleguide/badge/?version=latest)](https://wemake-python-styleguide.readthedocs.io/en/latest/?badge=latest)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/wemake-services/wemake-python-styleguide/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/wemake-services/wemake-python-styleguide.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/wemake-services/wemake-python-styleguide/context:python)\n---\n\nWelcome to the strictest and most opinionated python linter ever.\n\n`wemake-python-styleguide` is actually a `flake8` plugin\nwith some other plugins as dependencies.\n\n```text\nThe Zen of Python, by Tim Peters\n\nBeautiful is better than ugly.\nExplicit is better than implicit.\nSimple is better than complex.\nComplex is better than complicated.\nFlat is better than nested.\nSparse is better than dense.\nReadability counts.\nSpecial cases aren\'t special enough to break the rules.\nAlthough practicality beats purity.\nErrors should never pass silently.\nUnless explicitly silenced.\nIn the face of ambiguity, refuse the temptation to guess.\nThere should be one-- and preferably only one-- obvious way to do it.\nAlthough that way may not be obvious at first unless you\'re Dutch.\nNow is better than never.\nAlthough never is often better than *right* now.\nIf the implementation is hard to explain, it\'s a bad idea.\nIf the implementation is easy to explain, it may be a good idea.\nNamespaces are one honking great idea -- let\'s do more of those!\n```\n\n## Installation\n\n```bash\npip install wemake-python-styleguide\n```\n\nYou will also need to create a `setup.cfg` file with [the following contents](https://wemake-python-styleguide.readthedocs.io/en/latest/pages/options/config.html#plugins).\n\nThis file is required to configure our linter and all 3rd party plugins it uses.\nHowever, this is a temporary solution.\nWe are working at providing the required configuration for you in the future.\n\nRunning:\n\n```bash\nflake8 your_module.py\n```\n\nThis app is still just good old `flake8`!\nAnd it won\'t change your existing workflow.\n\nSee ["Usage" section](https://wemake-python-styleguide.readthedocs.io/en/latest/pages/usage/setup.html)\nin the docs for examples and integrations.\n\n\n## What we are about\n\nWe have several primary objectives:\n\n0. Enforce `python3.6+` usage\n1. Significantly reduce complexity of your code and make it more maintainable\n2. Enforce "There should be one-- and preferably only one --obvious way to do it" rule to coding and naming styles\n3. Protect developers from possible errors and enforce best practices\n\nYou can find all error codes and plugins [in the docs](https://wemake-python-styleguide.readthedocs.io/en/latest/pages/violations/index.html).\n\n\n## What we are not\n\nWe are *not* planning to do the following things:\n\n0. Assume or check types, use `mypy` instead\n1. Reformat code, since we believe that developers should do that\n2. Check for `SyntaxError` or exceptions, write tests instead\n3. Appeal to everyone, this is **our** linter. But, you can [switch off](https://wemake-python-styleguide.readthedocs.io/en/latest/pages/usage/setup.html#ignoring-violations) any rules that you don\'t like\n\n\n## Show your style\n\nIf you use our linter - it means that your code is awesome.\nYou can be proud of it!\nAnd you should share your accomplishment with others\nby including a badge to your `README` file.\n\nIt looks like this:\n\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n### Markdown\n\n```\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n```\n\n### Restructured text\n\n```\n.. image:: https://img.shields.io/badge/style-wemake-000000.svg\n    :target: https://github.com/wemake-services/wemake-python-styleguide\n```\n\n\n## Contributing\n\nWe warmly welcome all contributions!\n\nSee ["Contributing"](https://wemake-python-styleguide.readthedocs.io/en/latest/pages/contributing.html)\nsection in the documentation if you want to contribute.\nYou can start with [issues that need some help](https://github.com/wemake-services/wemake-python-styleguide/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) right now.\n',
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://wemake-python-styleguide.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
