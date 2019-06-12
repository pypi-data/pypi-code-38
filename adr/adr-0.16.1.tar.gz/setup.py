# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['adr', 'adr.export', 'adr.util', 'app', 'recipes']

package_data = \
{'': ['*'], 'app': ['static/*', 'templates/*'], 'recipes': ['queries/*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'cachy>=0.2.0,<0.3.0',
 'docutils>=0.14,<0.15',
 'flask>=1.0.2,<2.0.0',
 'json-e>=3.0.0,<4.0.0',
 'loguru>=0.2.5,<0.3.0',
 'markdown>=3.0.1,<4.0.0',
 'orderedset>=2.0.1,<3.0.0',
 'pygments>=2.3.1,<3.0.0',
 'pyyaml>=5.1,<6.0',
 'requests>=2.21.0,<3.0.0',
 'terminaltables>=3.1.0,<4.0.0',
 'tomlkit>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['adr = adr.cli:main',
                     'adr-app = app.app:main',
                     'adr-gist = adr.export.gist:cli',
                     'adr-test = adr.export.test:cli']}

setup_kwargs = {
    'name': 'adr',
    'version': '0.16.1',
    'description': 'Utility for running ActiveData recipes',
    'long_description': '[![Build Status](https://travis-ci.org/mozilla/adr.svg?branch=master)](https://travis-ci.org/mozilla/adr)\n[![PyPI version](https://badge.fury.io/py/adr.svg)](https://badge.fury.io/py/adr)\n[![PyPI version](https://readthedocs.org/projects/active-data-recipes/badge/?version=latest)](https://active-data-recipes.readthedocs.io)\n\n# adr\n\nThis is the runner for [ActiveData recipes][0], it provides a command line interface and flask web\napp. [ActiveData][1] is a large data warehouse containing billions of records related to Mozilla\'s\nCI, version control, bug tracking and much more. An ActiveData "recipe" is a Python snippet that\nruns one or more queries against ActiveData, then performs some post-processing before returning the\nresults.\n\nOther than a handful of built-in recipes, this repo doesn\'t contain any actual recipes itself. Those\nlive in project specific repositories that will typically depend on some version of this library.\nThe recommended way to run a recipe is to follow the README of the desired recipe project rather\nthan starting here.\n\n\n# Known Recipe Projects\n\nHere are some of the known repositories containing ActiveData recipes:\n\n* [active-data-recipes][2] - Misc recipes that are mostly untriaged. Good for finding examples to\n  copy from.\n\n\n# Installation\n\nAlthough installing `adr` directly is not recommended, it is still supported:\n\n    $ pip install adr\n\nYou will need Python 3.6 or higher.\n\n\n# Usage\n\nThe `adr` binary will search for recipes that live under $CWD, so usually just changing directories\nto the repository containing recipes is the best way to ensure `adr` can discover them.\n\nFor a list of available recipes:\n\n    $ adr --list\n\nTo run a given recipe:\n\n    $ adr <recipe> <options>\n\nFor recipe specific options see:\n\n    $ adr <recipe> -- --help\n\n\n# Contributing\n\nTo contribute to `adr` first [install poetry][3], then run:\n\n    $ git clone https://github.com/mozilla/adr\n    $ cd adr\n    $ poetry install\n\nNow you can use `poetry run` to perform various development commands:\n\n    # run adr\n    $ poetry run adr <recipe>\n\n    # run webapp\n    $ poetry run adr-app\n\n    # run tests\n    $ poetry run tox\n\nAlternatively activate the `poetry` shell ahead of time:\n\n    $ poetry shell\n\n    # run adr\n    $ adr <recipe>\n\n    # run app\n    $ adr-app\n\n    # run tests\n    $ tox\n\n[0]: https://active-data-recipes.readthedocs.io\n[1]: https://github.com/mozilla/ActiveData\n[2]: https://github.com/mozilla/active-data-recipes\n[3]: https://poetry.eustace.io/docs/#installation\n',
    'author': 'Andrew Halberstadt',
    'author_email': 'ahalberstadt@mozilla.com',
    'url': 'https://github.com/mozilla/adr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
