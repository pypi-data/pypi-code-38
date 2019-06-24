# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ogma', 'ogma.commands', 'ogma.modelutils', 'ogma.templates', 'ogma.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=0.9,<0.10',
 'SQLAlchemy>=1.3,<1.4',
 'argcomplete>=1.10,<1.11',
 'colorama>=0.4,<0.5',
 'colored>=1.3,<1.4',
 'pystache>=0.5,<0.6']

entry_points = \
{'console_scripts': ['ogma = ogma:main']}

setup_kwargs = {
    'name': 'ogma',
    'version': '0.1.0',
    'description': 'Ogma: A database access code generator for Java',
    'long_description': "# Ogma\n\n> According to legend, he is the inventor of Ogham, the runic language in which Irish Gaelic was first written. \n\n**Ogma** is a database access code generator for Java. It will take your database schema definition written in a Python-based DSL and generate (with jOOQ, among others) the necessary Java code to perform typed queries on that database.\n\nIt can also generate the necessary DDL to create the database structure according to spec.\n\n*Ogma* has been written for MySQL and MariaDB, but could be made to work with other engines that are both supported by SQLAlchemy and jOOQ.\n\n# How to install\n\nJust run the usual for a Python package:\n\n```bash\npip install ogma\n```\n\nThen you can run `ogma`.\n\n# Code generation and other tools\n\n*Ogma* obviously generates code, but it can also do other things. The tool is organized with subcommands.\n\n## Generation\n\nThe `generate` subcommand is used to generate Java code from the model file. The model file is a Python with some restrictions and additions:\n\n1. There is an implicit import of everything from `modelutils`\n1. No imports are allowed\n\n# For Developers\n## Structure\n * `modelutils` contains all the code that is imported into the database model files and that internally deals with model operations.\n * `commands` contains the entry points for the tool's subcommands\n * `templates` contains *mustache* templates for jOOQ's configuration and additional generated Java code\n\n",
    'author': 'Jacobo de Vera',
    'author_email': 'devel@jacobodevera.com',
    'url': 'https://www.github.com/jdevera/ogma',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
