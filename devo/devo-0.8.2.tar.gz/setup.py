# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['devo', 'devo.create', 'devo.generate', 'devo.gitlab', 'devo.kube']

package_data = \
{'': ['*'],
 'devo': ['templates/ci/*',
          'templates/k8s/base/*',
          'templates/k8s/base/app/*',
          'templates/k8s/base/db/*',
          'templates/k8s/prod/*',
          'templates/k8s/stage/*',
          'templates/k8s/test/*',
          'templates/project/*',
          'templates/project/requirements/*',
          'templates/project/scripts/*',
          'templates/project/src/*',
          'templates/project/tests/*',
          'templates/skaffold/*']}

install_requires = \
['click>=7.0,<8.0',
 'jinja2>=2.10,<3.0',
 'python-gitlab>=1.8,<2.0',
 'ruamel.yaml>=0.15.94,<0.16.0']

entry_points = \
{'console_scripts': ['devo = devo.main:cli']}

setup_kwargs = {
    'name': 'devo',
    'version': '0.8.2',
    'description': '',
    'long_description': None,
    'author': 'Dominic Werner',
    'author_email': 'aka.vince@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
