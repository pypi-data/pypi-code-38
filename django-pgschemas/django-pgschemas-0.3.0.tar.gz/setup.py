# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_pgschemas',
 'django_pgschemas.contrib',
 'django_pgschemas.contrib.channels',
 'django_pgschemas.management',
 'django_pgschemas.management.commands',
 'django_pgschemas.postgresql_backend',
 'django_pgschemas.test']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.0,<3.0', 'psycopg2>=2.7,<3.0']

setup_kwargs = {
    'name': 'django-pgschemas',
    'version': '0.3.0',
    'description': 'Multi-tenancy on Django using PostgreSQL schemas.',
    'long_description': 'django-pgschemas\n================\n\n.. image:: https://img.shields.io/badge/packaging-poetry-purple.svg\n   :alt: Packaging: poetry\n   :target: https://github.com/sdispater/poetry\n\n.. image:: https://img.shields.io/badge/code%20style-black-black.svg\n   :alt: Code style: black\n   :target: https://github.com/ambv/black\n\n.. image:: https://badges.gitter.im/Join%20Chat.svg\n   :alt: Join the chat at https://gitter.im/django-pgschemas\n   :target: https://gitter.im/django-pgschemas/community?utm_source=share-link&utm_medium=link&utm_campaign=share-link\n\n.. image:: https://api.travis-ci.org/lorinkoz/django-pgschemas.svg?branch=master\n   :alt: Build status\n   :target: https://travis-ci.org/lorinkoz/django-pgschemas\n\n.. image:: https://readthedocs.org/projects/django-pgschemas/badge/?version=latest\n    :alt: Documentation status\n    :target: https://django-pgschemas.readthedocs.io/\n\n.. image:: https://codecov.io/gh/lorinkoz/django-pgschemas/branch/master/graphs/badge.svg?branch=master\n    :alt: Code coverage\n    :target: https://codecov.io/gh/lorinkoz/django-pgschemas\n\n.. image:: https://badge.fury.io/py/django-pgschemas.svg\n    :alt: PyPi version\n    :target: http://badge.fury.io/py/django-pgschemas\n\n|\n\nThis app uses PostgreSQL schemas to support data multi-tenancy in a single\nDjango project. It is a fork of `django-tenants`_ with some conceptual changes:\n\n- There are static tenants and dynamic tenants. Static tenants can have their\n  own apps and urlconf.\n- Tenants are routed both via subdomain and via subfolder on shared subdomain.\n- Public is no longer the schema for storing the main site data. Public should\n  be used only for true shared data across all tenants. Table "overriding" via\n  search path is no longer encouraged.\n- Management commands can be run on multiple schemas via wildcards - the\n  multiproc behavior of migrations was extended to just any tenant command.\n\n.. _django-tenants: https://github.com/tomturner/django-tenants\n\n\nDocumentation\n-------------\n\nhttps://django-pgschemas.readthedocs.io/\n\nContributing\n------------\n\n- Join the discussion at https://gitter.im/django-pgschemas/community.\n- PRs are welcome! If you have questions or comments, please use the link\n  above.\n- Django\'s code of conduct applies to all means of contribution.\n  https://www.djangoproject.com/conduct/.\n\nCredits\n-------\n\n* Tom Turner for ``django-tenants``\n* Bernardo Pires for ``django-tenant-schemas``\n* Vlada Macek for ``django-schemata``\n',
    'author': 'Lorenzo Peña',
    'author_email': 'lorinkoz@gmail.com',
    'url': 'https://github.com/lorinkoz/django-pgschemas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
