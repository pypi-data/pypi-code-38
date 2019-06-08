# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['agora_community_sdk']

package_data = \
{'': ['*'], 'agora_community_sdk': ['frontend/*', 'frontend/.vscode/*']}

install_requires = \
['nest_asyncio>=1.0,<2.0', 'pyppeteer>=0.0.25,<0.0.26', 'websockets==6.0']

setup_kwargs = {
    'name': 'agora-community-sdk',
    'version': '0.1.6',
    'description': 'An SDK allowing the use of Agora SDK in python',
    'long_description': None,
    'author': 'samyak-jain',
    'author_email': 'samtan106@gmail.com',
    'url': 'https://github.com/samyak-jain/AgoraPython',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
