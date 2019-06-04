# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['commitizen',
 'commitizen.commands',
 'commitizen.cz',
 'commitizen.cz.conventional_commits',
 'commitizen.cz.jira']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'decli>=0.5.0,<0.6.0',
 'packaging>=19.0,<20.0',
 'questionary>=1.0,<2.0',
 'termcolor>=1.1,<2.0',
 'tomlkit>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['cz = commitizen.cli:main']}

setup_kwargs = {
    'name': 'commitizen',
    'version': '1.5.1',
    'description': 'Python commitizen client tool',
    'long_description': '=============\nCommitizen\n=============\n\n    Python 3 command line utility to standardize commit messages and bump version\n\n\n.. image:: https://img.shields.io/travis/Woile/commitizen.svg?style=flat-square\n    :alt: Travis\n    :target: https://travis-ci.org/Woile/commitizen\n\n.. image:: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square\n    :alt: Conventional Commits\n    :target: https://conventionalcommits.org\n\n.. image:: https://img.shields.io/pypi/v/commitizen.svg?style=flat-square\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/project/commitizen/\n\n..  image:: https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square\n    :alt: Supported versions\n    :target: https://pypi.org/project/commitizen/\n\n.. image:: https://img.shields.io/codecov/c/github/Woile/commitizen.svg?style=flat-square\n    :alt: Codecov\n    :target: https://codecov.io/gh/Woile/commitizen\n\n.. image:: docs/images/demo.gif\n    :alt: Example running commitizen\n\n--------------\n\n**Documentation**: https://Woile.github.io/commitizen/\n\n--------------\n\n.. contents::\n    :depth: 2\n\n\nAbout\n==========\n\nCommitizen is a tool designed for teams.\n\nIts main purpose is to define a standard way of commiting rules\nand communicating it (using the cli provided by commitizen).\n\nThe reasoning behind it is that is easier to read, and enforces writing\ndescriptive commits.\n\nBesides that, having a convetion on your commits, makes it possible to\nparse them and use them for something else, like generating automatically\nthe version or a changelog.\n\n\nInstallation\n=============\n\n::\n\n    pip install -U commitizen\n\n::\n\n    poetry add commitizen --dev\n\n\n**Global installation**\n\n::\n\n    sudo pip3 install -U commitizen\n\nFeatures\n========\n\n- Command line utility to create commits with your rules. Defaults: `conventional commits`_\n- Display information about your commit rules (commands: schema, example, info)\n- Bump version automatically using semantic verisoning based on the commits. `Read More <./docs/bump.md>`_\n- Generate a changelog using "Keep a changelog" (Planned feature)\n\n\nCommit rules\n============\n\nThis client tool prompts the user with information about the commit.\n\nBased on `conventional commits`_\n\nThis is an example of how the git messages history would look like:\n\n::\n\n    fix: minor typos in code\n    feat: new command update\n    docs: improved commitizens tab in readme\n    feat(cz): jira smart commits\n    refactor(cli): renamed all to ls command\n    feat: info command for angular\n    docs(README): added badges\n    docs(README): added about, installation, creating, etc\n    feat(config): new loads from ~/.cz and working project .cz .cz.cfg and setup.cfg\n\nAnd then using ``cz bump`` you can change the version of your project\n\n``feat`` to ``MINOR``\n``fix`` to ``PATCH``\n\n\nCommitizens\n===========\n\nThese are the available commiting styles by default:\n\n* cz_conventional_commits: `conventional commits`_\n* cz_jira: `jira smart commits <https://confluence.atlassian.com/fisheye/using-smart-commits-298976812.html>`_\n\n\nThe installed ones can be checked with:\n\n::\n\n    cz ls\n\n\n\nCommiting\n=========\n\nRun in your terminal\n\n::\n\n    cz commit\n\nor the shortcut\n\n::\n\n    cz c\n\n\nUsage\n=====\n\n::\n\n    $ cz --help\n    usage: cz [-h] [--debug] [-n NAME] [--version]\n            {ls,commit,c,example,info,schema,bump} ...\n\n    Commitizen is a cli tool to generate conventional commits.\n    For more information about the topic go to https://conventionalcommits.org/\n\n    optional arguments:\n    -h, --help            show this help message and exit\n    --debug               use debug mode\n    -n NAME, --name NAME  use the given commitizen\n    --version             get the version of the installed commitizen\n\n    commands:\n    {ls,commit,c,example,info,schema,bump}\n        ls                  show available commitizens\n        commit (c)          create new commit\n        example             show commit example\n        info                show information about the cz\n        schema              show commit schema\n        bump                bump semantic version based on the git log\n\nContributing\n============\n\nFeel free to create a PR.\n\n1. Clone the repo.\n2. Add your modifications\n3. Create a virtualenv\n4. Run :code:`./scripts/test`\n\n\n.. _conventional commits: https://conventionalcommits.org/',
    'author': 'Santiago Fraire',
    'author_email': 'santiwilly@gmail.com',
    'url': 'https://github.com/woile/commitizen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
