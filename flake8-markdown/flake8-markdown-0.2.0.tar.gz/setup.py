# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flake8_markdown']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.7,<4.0']

entry_points = \
{'console_scripts': ['flake8-markdown = flake8_markdown:main']}

setup_kwargs = {
    'name': 'flake8-markdown',
    'version': '0.2.0',
    'description': 'Lints Python code blocks in Markdown files using flake8',
    'long_description': '# Flake8 Markdown\n\n[\n![PyPI](https://img.shields.io/pypi/v/flake8-markdown.svg)\n![PyPI](https://img.shields.io/pypi/pyversions/flake8-markdown.svg)\n![PyPI](https://img.shields.io/github/license/johnfraney/flake8-markdown.svg)\n](https://pypi.org/project/flake8-markdown/)\n[![TravisCI](https://travis-ci.org/johnfraney/flake8-markdown.svg?branch=master)](https://travis-ci.org/johnfraney/flake8-markdown)\n\nFlake8 Markdown lints [GitHub-style Python code blocks](https://help.github.com/en/articles/creating-and-highlighting-code-blocks#fenced-code-blocks) in Markdown files using [`flake8`](https://flake8.readthedocs.io/en/stable/).\n\nThis package helps improve a Python project\'s documentation by ensuring that code samples are error-free.\n\n## Features\n\n- Lints code blocks containing regular Python and Python interpreter code ([`pycon`](http://pygments.org/docs/lexers/#pygments.lexers.python.PythonConsoleLexer))\n- [pre-commit](#pre-commit-hook) hook to lint on commit\n\n## Installation\n\nFlake8 Markdown can be installed from PyPI using `pip` or your package manager of choice:\n\n```\npip install flake8-markdown\n```\n\n## Usage\n\n### CLI\n\nYou can use Flake8 Markdown as a CLI tool using the `flake8-markdown` command.\n\n`flake8-markdown` accepts one or more [globs](https://docs.python.org/3.7/library/glob.html) as its arguments.\n\nExample:\n\n```console\n$ flake8-markdown flake8-markdown "tests/samples/*.md"\ntests/samples/emphasized_lines.md:6:1: F821 undefined name \'emphasized_imaginary_function\'\ntests/samples/basic.md:8:48: E999 SyntaxError: EOL while scanning string literal\ntests/samples/basic.md:14:7: F821 undefined name \'undefined_variable\'\n```\n\n### pre-commit hook\n\nYou can also add `flake8-markdown` to your project using [pre-commit](https://pre-commit.com/). When configured, any staged Markdown files will be linted using `flake8-markdown` once you run `git commit`.\n\nTo enable this hook in your local repository, add the following `repo` to your `.pre-commit-config.yaml` file:\n\n```yaml\n# .pre-commit-config.yaml\nrepos:\n  - repo: https://github.com/johnfraney/flake8-markdown\n    rev: v0.2.0\n    hooks:\n      - id: flake8-markdown\n```\n\n## Code of Conduct\n\nEveryone interacting in the project\'s codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).\n\n## History\n\n## [0.2.0] - 2019-06-14\n\n### Added\n\n- [`pycon`](http://pygments.org/docs/lexers/#pygments.lexers.python.PythonConsoleLexer) code block support\n\n### [0.1.1] - 2019-05-19\n\n#### Changed\n\n- Fixed pre-commit example in README\n\n### [0.1.0] - 2019-05-19\n\n#### Added\n\n- Added code for initial release\n',
    'author': 'John Franey',
    'author_email': 'johnfraney@gmail.com',
    'url': 'https://github.com/johnfraney/flake8-markdown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
