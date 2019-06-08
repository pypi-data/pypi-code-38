# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pugsql']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'pugsql',
    'version': '0.1.8',
    'description': 'PugSQL is an anti-ORM that facilitates interacting with databases using SQL in files.',
    'long_description': "[PugSQL](https://pugsql.org) is a simple Python interface for using parameterized SQL, in files, with [any  SQLAlchemy-supported database](https://docs.sqlalchemy.org/en/13/dialects/index.html).\n\nFor more information and full documentation, visit [pugsql.org](https://pugsql.org).\n\n```\nimport pugsql\n\n# Create a module of database functions from a set of sql files on disk.\nqueries = pugsql.module('resources/sql')\n\n# Point the module at your database.\nqueries.connect('sqlite:///foo.db')\n\n# Invoke parameterized queries, receive dicts!\nuser = queries.find_user(user_id=42)\n\n# -> { 'user_id': 42, 'username': 'mcfunley' }\n```\n\nIn the example above, the query would be specified like this:\n\n```\n--- :name find_user :one\nselect * from users where user_id = :user_id\n```\n\nSo _throw away_ your bulky ORM and talk to your database the way the gods intended! Install PugSQL today!\n",
    'author': 'Dan McKinley',
    'author_email': 'mcfunley@gmail.com',
    'url': 'https://pugsql.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
