# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dh_potluck']

package_data = \
{'': ['*']}

install_requires = \
['Werkzeug>=0.15.0',
 'boltons>=19.1,<20.0',
 'ddtrace>=0.25.0',
 'flask>=1.0,<2.0',
 'marshmallow>=2.19,<3.0',
 'requests>=2.22,<3.0',
 'sqlalchemy>=1.3,<2.0',
 'webargs>=5.3,<6.0']

setup_kwargs = {
    'name': 'dh-potluck',
    'version': '0.1.7',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
