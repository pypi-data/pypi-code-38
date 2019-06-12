# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['content_size_limit_asgi']

package_data = \
{'': ['*']}

install_requires = \
['starlette>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'content-size-limit-asgi',
    'version': '0.1.1',
    'description': 'An ASGI3 middleware to implement maximum content size limits (mostly useful for HTTP uploads)',
    'long_description': None,
    'author': 'Steinn Eldjárn Sigurðarson',
    'author_email': 'steinnes@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
