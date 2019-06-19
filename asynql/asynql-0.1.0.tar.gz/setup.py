# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['asynql']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=0.28.0,<0.29.0', 'typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'asynql',
    'version': '0.1.0',
    'description': 'AsyncIO GraphQL client',
    'long_description': "[![GraphQL logo](https://raw.githubusercontent.com/k8s-team/asynql/master/logo.png)](https://github.com/k8s-team/asynql)\n\n# asynql\n\nAsyncio `GraphQL` client\n\n## Usage\n\n```python\nfrom asynql import GQLModel\n\nclass Address(GQLModel):\n    __one__ = 'address'\n    __many__ = 'addresses'\n\n    lat: float\n    lon: float\n    city: str\n    line: str\n```\n\nWe need `__one__` and `__many__` to be specified to customize query for one item or for many items.\n",
    'author': 'Vladimir Puzakov',
    'author_email': 'vppuzakov@gmail.com',
    'url': 'https://asynql.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
