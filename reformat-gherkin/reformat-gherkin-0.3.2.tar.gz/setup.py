# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reformat_gherkin', 'reformat_gherkin.ast_node']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'cattrs>=0.9.0,<0.10.0',
 'click>=7.0,<8.0',
 'gherkin-official>=4.1,<5.0',
 'pyyaml>=5.1,<6.0']

entry_points = \
{'console_scripts': ['reformat-gherkin = reformat_gherkin.cli:main']}

setup_kwargs = {
    'name': 'reformat-gherkin',
    'version': '0.3.2',
    'description': 'Formatter for Gherkin language',
    'long_description': "# Reformat-gherkin\n\n[![Build Status](https://travis-ci.com/ducminh-phan/reformat-gherkin.svg?branch=master)](https://travis-ci.com/ducminh-phan/reformat-gherkin) [![Coverage Status](https://coveralls.io/repos/github/ducminh-phan/reformat-gherkin/badge.svg?branch=master)](https://coveralls.io/github/ducminh-phan/reformat-gherkin?branch=master) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![PyPI](https://img.shields.io/pypi/v/reformat-gherkin.svg)](https://pypi.org/project/reformat-gherkin/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black) [![Maintainability](https://api.codeclimate.com/v1/badges/16718a231901c293215d/maintainability)](https://codeclimate.com/github/ducminh-phan/reformat-gherkin/maintainability)\n\n## Table of Contents\n\n- [About](#about)\n- [Getting Started](#getting-started)\n- [Usage](#usage)\n- [Pre-commit hook](#pre-commit-hook)\n\n## About\n\nThis tool is a formatter for Gherkin files. It ensures consistent look regardless of the project and authors.\n\n`reformat-gherkin` can be used either as a command-line tool, or a `pre-commit` hook.\n\n## Getting Started\n\nThese instructions will get you a copy of the project up and running on your local machine for development and testing purposes.\n\n### Prerequisites\n\n- [Python 3.6+](https://www.python.org/downloads/)\n- [Poetry](https://poetry.eustace.io/)\n\n### Installing\n\n- Clone this repository\n  ```bash\n  git clone https://github.com/ducminh-phan/reformat-gherkin.git\n  ```\n\n- Install dependencies\n  ```bash\n  poetry install\n  ```\n\n\n## Usage\n\n    Usage: reformat-gherkin [OPTIONS] [SRC]...\n    \n      Reformat the given Gherkin files and all files in the given directories\n      recursively.\n    \n    Options:\n      --check                       Don't write the files back, just return the\n                                    status. Return code 0 means nothing would\n                                    change. Return code 1 means some files would\n                                    be reformatted. Return code 123 means there\n                                    was an internal error.\n      -a, --alignment [left|right]  Specify the alignment of step keywords (Given,\n                                    When, Then,...). If specified, all statements\n                                    after step keywords are left-aligned, spaces\n                                    are inserted before/after the keywords to\n                                    right/left align them. By default, step\n                                    keywords are left-aligned, and there is a\n                                    single space between the step keyword and the\n                                    statement.\n      --fast / --safe               If --fast given, skip the sanity checks of\n                                    file contents. [default: --safe]\n      --config FILE                 Read configuration from FILE.\n      --version                     Show the version and exit.\n      --help                        Show this message and exit.\n      \n### Config file\n\nThe tool is able to read project-specific default values for its command line options from a `.reformat-gherkin.yaml` file.\n\nBy default, `reformat-gherkin` looks for the config file starting from the common base directory of all files and directories passed on the command line. If it's not there, it looks in parent directories. It stops looking when it finds the file, or a .git directory, or a .hg directory, or the root of the file system, whichever comes first.\n\nExample config file\n\n```yaml\ncheck: False\nalignment: left\n```\n\n## Pre-commit hook\n\nOnce you have installed [pre-commit](https://pre-commit.com/), add this to the `.pre-commit-config.yaml` in your repository:\n\n    repos:\n      - repo: https://github.com/ducminh-phan/reformat-gherkin\n        rev: stable\n        hooks:\n          - id: reformat-gherkin\n\nThen run `pre-commit install` and you're ready to go.\n",
    'author': 'Duc-Minh Phan',
    'author_email': 'alephvn@gmail.com',
    'url': 'https://github.com/ducminh-phan/reformat-gherkin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
