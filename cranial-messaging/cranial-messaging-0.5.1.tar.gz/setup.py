# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cranial',
 'cranial.connectors',
 'cranial.keyvalue',
 'cranial.listeners',
 'cranial.messaging']

package_data = \
{'': ['*'],
 'cranial': ['common/*',
             'datastore/*',
             'datastore/adapters/*',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_12131_15.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.base.py@neomake_25770_2.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/.marathon.py@neomake_12131_24.py',
             'servicediscovery/base.py',
             'servicediscovery/base.py',
             'servicediscovery/base.py',
             'servicediscovery/base.py',
             'servicediscovery/base.py',
             'servicediscovery/base.py',
             'servicediscovery/echo.py',
             'servicediscovery/echo.py',
             'servicediscovery/echo.py',
             'servicediscovery/echo.py',
             'servicediscovery/echo.py',
             'servicediscovery/echo.py',
             'servicediscovery/marathon.py',
             'servicediscovery/marathon.py',
             'servicediscovery/marathon.py',
             'servicediscovery/marathon.py',
             'servicediscovery/marathon.py',
             'servicediscovery/marathon.py'],
 'cranial.messaging': ['adapters/*', 'test/test_coordinator.py']}

install_requires = \
['boto3>=1.9,<2.0',
 'cachetools>=3.1.1,<4.0.0',
 'docopt>=0.6.2,<0.7.0',
 'psycopg2-binary>=2.6.2,<3.0.0',
 'pyyaml>=5.1,<6.0',
 'recordclass>=0.11.1,<0.12.0',
 'requests-futures>=0.9.7,<0.10.0',
 'smart_open>=1.8.3,<2.0.0',
 'ujson>=1.3.5,<2.0.0',
 'zmq>=0.0.0,<0.0.1']

setup_kwargs = {
    'name': 'cranial-messaging',
    'version': '0.5.1',
    'description': 'Abstractions for high-level communication between micro-services.',
    'long_description': None,
    'author': 'Matt Chapman et al.',
    'author_email': 'Matt@NinjitsuWeb.com',
    'url': 'https://github.com/tribune/cranial-messaging',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
