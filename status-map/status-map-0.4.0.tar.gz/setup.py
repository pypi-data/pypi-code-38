# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['status_map']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.3,<3.0']

setup_kwargs = {
    'name': 'status-map',
    'version': '0.4.0',
    'description': 'Status map (and its transitions) data structure',
    'long_description': None,
    'author': 'Luiz Menezes',
    'author_email': 'luiz.menezesf@gmail.com',
    'url': 'https://github.com/lamenezes/django-choices-enum',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
