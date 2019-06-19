# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tormor']

package_data = \
{'': ['*'],
 'tormor': ['tests/*',
            'tests/Schema/customer/*',
            'tests/Schema/employee/*',
            'tests/Schema/product/*',
            'tests/Schema2/department/*']}

install_requires = \
['asyncpg>=0.18.3,<0.19.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['tormor = tormor.main_script:script']}

setup_kwargs = {
    'name': 'tormor',
    'version': '2.0',
    'description': 'Postgres migration library',
    'long_description': None,
    'author': 'Tle Ekkul',
    'author_email': 'aryuth.ekkul@proteus-tech.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
