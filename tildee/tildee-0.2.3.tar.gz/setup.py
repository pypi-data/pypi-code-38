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
    'version': '0.2.3',
    'description': 'A client for tildes.net',
    'long_description': 'This is tildee.py, a Python 3 library for interacting with the <https://tildes.net> API. Note that this API is not stable and not actually intended for external use, so this could break at any moment.\n\n[PyPI](https://pypi.org/project/tildee/) \xe2\x80\x94 [Source](https://git.dingenskirchen.systems/Dingens/tildee.py) \xe2\x80\x94 [Docs](https://tildee.readthedocs.io/en/latest/index.html)\n',
    'author': 'deing',
    'author_email': 'admin@15318.de',
    'url': 'https://tildee.readthedocs.io/en/latest/index.html',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
