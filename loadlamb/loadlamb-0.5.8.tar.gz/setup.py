# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['loadlamb',
 'loadlamb.chalicelib',
 'loadlamb.chalicelib.contrib',
 'loadlamb.chalicelib.contrib.db',
 'loadlamb.chalicelib.contrib.requests',
 'loadlamb.chalicelib.tests',
 'loadlamb.chalicelib.tests.wsgi',
 'loadlamb.chalicelib.tests.wsgi.djangor',
 'loadlamb.chalicelib.tests.wsgi.djangor.accounts',
 'loadlamb.chalicelib.tests.wsgi.djangor.accounts.migrations',
 'loadlamb.chalicelib.tests.wsgi.djangor.djangor',
 'loadlamb.chalicelib.tests.wsgi.flaskr']

package_data = \
{'': ['*'],
 'loadlamb': ['.chalice/*'],
 'loadlamb.chalicelib': ['templates/*'],
 'loadlamb.chalicelib.tests.wsgi.djangor.accounts': ['fixtures/*'],
 'loadlamb.chalicelib.tests.wsgi.djangor.djangor': ['templates/*',
                                                    'templates/registration/*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'aiohttp>=3.5,<4.0',
 'base58>=1.0,<2.0',
 'beautifulsoup4>=4.7,<5.0',
 'boto3>=1.9,<2.0',
 'chalice>=1.8,<2.0',
 'docb>=1.1,<2.0',
 'jinja2>=2.10,<3.0',
 'python-slugify>=3.0,<4.0',
 'requests>=2.21,<3.0',
 'sammy>=0.4.3,<0.5.0',
 'unipath>=1.1,<2.0',
 'warrant-lite>=1.0,<2.0']

entry_points = \
{'console_scripts': ['loadlamb = loadlamb.chalicelib.cli:loadlamb']}

setup_kwargs = {
    'name': 'loadlamb',
    'version': '0.5.8',
    'description': 'Load testing library built to run on AWS Lambda',
    'long_description': None,
    'author': 'Brian Jinwright',
    'author_email': 'brian@ipoots.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
