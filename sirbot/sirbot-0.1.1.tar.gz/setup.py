# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sirbot',
 'sirbot.endpoints',
 'sirbot.plugins',
 'sirbot.plugins.apscheduler',
 'sirbot.plugins.github',
 'sirbot.plugins.postgres',
 'sirbot.plugins.readthedocs',
 'sirbot.plugins.slack']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.4.0,<0.5.0',
 'aiohttp>=3.4,<4.0',
 'apscheduler>=3.5,<4.0',
 'asyncio-contextmanager>=1.0,<2.0',
 'asyncpg>=0.18.2,<0.19.0',
 'gidgethub>=3.0,<4.0',
 'slack-sansio>=1.0.0,<2.0.0',
 'ujson>=1.35,<2.0']

setup_kwargs = {
    'name': 'sirbot',
    'version': '0.1.1',
    'description': 'The good Sir Bot-a-lot. An asynchronous python bot framework.',
    'long_description': None,
    'author': 'Ovv',
    'author_email': 'contact@ovv.wtf',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
