# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cranial', 'cranial.listeners', 'cranial.messaging']

package_data = \
{'': ['*'],
 'cranial': ['servicediscovery/*'],
 'cranial.messaging': ['adapters/*', 'test/*']}

install_requires = \
['boto3>=1.9,<2.0',
 'cachetools>=2.1,<3.0',
 'cranial-common>=0.3.0,<0.4.0',
 'psycopg2>=2.6.2,<3.0.0',
 'recordclass>=0.11.1,<0.12.0',
 'requests-futures>=0.9.7,<0.10.0',
 'smart_open>=1.8.3,<2.0.0',
 'ujson>=1.3.5,<2.0.0',
 'zmq>=0.0.0,<0.0.1']

setup_kwargs = {
    'name': 'cranial-messaging',
    'version': '0.4.0.dev0',
    'description': 'Abstractions for high-level communication between micro-services.',
    'long_description': None,
    'author': 'Matt Chapman et al.',
    'author_email': 'Matt@NinjitsuWeb.com',
    'url': 'https://github.com/tribune/cranial-messaging',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
