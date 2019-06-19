# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['git_repo_backup']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'gitpython>=2.1,<3.0',
 'pygithub>=1.43,<2.0',
 'tqdm>=4.32,<5.0']

entry_points = \
{'console_scripts': ['git-backup = git_repo_backup.backup:cli']}

setup_kwargs = {
    'name': 'git-repo-backup',
    'version': '2.0.0',
    'description': 'Backups all of your remote GitHub repositories locally.',
    'long_description': '# Git backup.\n\nBackups all of your GitHub remote git repositories locally.\n\n## What do I need?\n- Python 3+\n\n## How to run it?\n1. Set `GITHUB_TOKEN` env variable with your github token\n\n2. Execute script with path to where repositories should be saved\n```\ngit-backup --path=~/Documents/backup\n```\n\n## Install with pypi\n```\n$ pip install git-repo-backup\n```\n',
    'author': 'whisller',
    'author_email': 'whisller@gmail.com',
    'url': 'https://github.com/whisller/git-repo-backup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
