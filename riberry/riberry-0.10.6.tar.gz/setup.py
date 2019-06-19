# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['riberry',
 'riberry.app',
 'riberry.app.actions',
 'riberry.app.addons',
 'riberry.app.backends',
 'riberry.app.backends.impl',
 'riberry.app.backends.impl.celery',
 'riberry.app.backends.impl.celery.addons',
 'riberry.app.backends.impl.celery.addons.capacity',
 'riberry.app.context',
 'riberry.app.misc',
 'riberry.app.util',
 'riberry.celery',
 'riberry.celery.background',
 'riberry.celery.background.events',
 'riberry.celery.client',
 'riberry.celery.client.dynamic',
 'riberry.celery.client.scale',
 'riberry.model',
 'riberry.model.application',
 'riberry.model.auth',
 'riberry.model.group',
 'riberry.model.interface',
 'riberry.model.job',
 'riberry.model.misc',
 'riberry.plugins',
 'riberry.plugins.defaults',
 'riberry.policy',
 'riberry.services',
 'riberry.util']

package_data = \
{'': ['*']}

install_requires = \
['celery[redis]>=4.3,<5.0',
 'click>=7.0,<8.0',
 'croniter>=0.3.29,<0.4.0',
 'pendulum>=2.0,<3.0',
 'pyjwt>=1.7,<2.0',
 'pyyaml>=5.1,<6.0',
 'redis>=3.2,<4.0',
 'sqlalchemy>=1.3,<2.0',
 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'riberry',
    'version': '0.10.6',
    'description': 'Python-driven job management system',
    'long_description': '# Riberry\n\n[![CircleCI](https://circleci.com/gh/srafehi/riberry/tree/master.svg?style=svg)](https://circleci.com/gh/srafehi/riberry/tree/master)\n\nUnder active development\n\n[Documentation](https://riberry.app)',
    'author': 'Shady Rafehi',
    'author_email': 'shadyrafehi@gmail.com',
    'url': 'https://github.com/srafehi/riberry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
