# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['encapsia_api']

package_data = \
{'': ['*']}

install_requires = \
['requests[security]>=2.20,<3.0', 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'encapsia-api',
    'version': '0.1.16',
    'description': 'Client API for talking to an Encapsia system.',
    'long_description': '# Encapsia API Library\n\nREST API for working with Encapsia.\n\nSee https://www.encapsia.com.\n\n# Release checklist\n\n* Run: flake8 --ignore=E501 .\n* Run: black .\n* Run: isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width=88 -y\n* Ensure git tag, package version, and enacpsia_api.__version__ are all equal.',
    'author': 'Timothy Corbett-Clark',
    'author_email': 'timothy.corbettclark@gmail.com',
    'url': 'https://github.com/tcorbettclark/encapsia-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
