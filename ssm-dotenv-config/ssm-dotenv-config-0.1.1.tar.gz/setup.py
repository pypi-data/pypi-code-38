# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ssm_dotenv_config']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0',
 'python-dotenv>=0.10.2,<0.11.0',
 'ujson>=1.35,<2.0',
 'vital-tools>=0.1.13,<0.2.0']

setup_kwargs = {
    'name': 'ssm-dotenv-config',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Jared Lunde',
    'author_email': 'jared.lunde@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
