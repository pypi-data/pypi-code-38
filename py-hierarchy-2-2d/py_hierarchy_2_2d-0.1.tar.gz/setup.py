# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['py_hierarchy_2_2d', 'py_hierarchy_2_2d.tests']

package_data = \
{'': ['*']}

install_requires = \
['xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'py-hierarchy-2-2d',
    'version': '0.1',
    'description': '',
    'long_description': None,
    'author': 'joefromct',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
