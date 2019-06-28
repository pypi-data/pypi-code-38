# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['source_query_proxy', 'source_query_proxy.source']

package_data = \
{'': ['*']}

install_requires = \
['pylru==1.2.0', 'uvloop==0.12.2']

setup_kwargs = {
    'name': 'source-query-proxy',
    'version': '0.15.0',
    'description': 'Async proxy for Source Engine Query Protocol',
    'long_description': None,
    'author': 'spumer',
    'author_email': 'spumer-tm@yandex.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
