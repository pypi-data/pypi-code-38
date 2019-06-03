# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['create_flask_skeleton',
 'create_flask_skeleton.template',
 'create_flask_skeleton.template.app',
 'create_flask_skeleton.template.app.apps',
 'create_flask_skeleton.template.tests']

package_data = \
{'': ['*'], 'create_flask_skeleton.template.app': ['static/*', 'templates/*']}

install_requires = \
['click>=7.0,<8.0', 'jinja2>=2.10,<3.0', 'pyyaml>=3.13,<4.0']

entry_points = \
{'console_scripts': ['create-flask-skeleton = create_flask_skeleton:main']}

setup_kwargs = {
    'name': 'create-flask-skeleton',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Ryan Wang',
    'author_email': 'hwwangwang@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
