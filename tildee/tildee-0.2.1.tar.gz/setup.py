# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tildee']

package_data = \
{'': ['*']}

install_requires = \
['cssselect>=1.0,<2.0', 'lxml>=4.3,<5.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'tildee',
    'version': '0.2.1',
    'description': 'A client for tildes.net',
    'long_description': "This is tildee.py, a Python 3 library for interacting with the <https://tildes.net> API. Note that this API is not stable and not actually intended for external use, so this could break at any moment.\n\n## Capabilities\nCurrently tildee.py can parse posts and their comments, create comments, topics and messages, parse new messages and notifications, edit comment and topic contents, edit topic metadata and remove/lock topics and comments.\n\n## Dependencies\nThis uses [Poetry](https://poetry.eustace.io/) to manage dependencies and [Black](https://black.readthedocs.io/en/stable/index.html#) for formatting.\n\n## Development\nTo install dependencies, run `poetry install`. You can run a python shell in the environment using `poetry run python` (I'd recommend using `ipython`, too). Format your code before committing by running `black .`.\n",
    'author': 'deing',
    'author_email': 'admin@15318.de',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
