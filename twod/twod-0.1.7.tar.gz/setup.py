# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['twod']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'twod',
    'version': '0.1.7',
    'description': 'A two-dimensional geometry library for humans.',
    'long_description': '\ntwod - A Two-Dimensional Geomety Library for Humans™\n====================================================\n\n|pypi|  |license| |python| |coverage| |build|\n\n**twod** is a Python 3 package that supplies simple two dimensional geometric primitives. Primitives currently include:\n\n- twod.Point, a point class\n- twod.Rect, a rectangle class\n\nInstall\n-------\n\n1. Install using pip:\n\n.. code:: bash\n\t  \n\t  $ pip3 install twod\n\t  \n2. Install from Github using poetry_:\n\n.. code:: bash\n\n\t  $ git clone https://github.com/JnyJny/twod.git\n\t  $ cd twod; poetry install\n\t  \n   \n\nUninstall\n---------\n\nUninstall using pip:\n\n.. code:: bash\n\n\t  $ pip3 uninstall twod\n\nUsage\n-----\n\n``Missing``\n\n.. _poetry: https://pypi.org/project/poetry/\n\n.. |pypi| image:: https://img.shields.io/pypi/v/twod.svg?style=flat-square&label=version\n   :target: https://pypi.org/pypi/twod\n   :alt: Latest version released on PyPi\n\t \n.. |python| image:: https://img.shields.io/pypi/pyversions/twod.svg?style=flat-squre\n   :target: https://pypi.org/project/twod\n   :alt: Python Versions\n\t\t    \n.. |license| image:: https://img.shields.io/badge/license-apache-blue.svg?style=flat-square\n   :target: https://github.com/jnyjny/twod/blob/master/LICENSE\n   :alt: Apache License v2.0\n\n.. |coverage| image:: https://coveralls.io/repos/github/JnyJny/twod/badge.svg?branch=master\n   :target: https://coveralls.io/github/JnyJny/twod?branch=master\n   :alt: Code Coverage\n\n.. |build| image:: https://travis-ci.com/JnyJny/twod.svg?branch=master\n\t\t \n\t\t   \n\t \n\n\t \n',
    'author': 'jnyjny',
    'author_email': 'erik.oshaughnessy@gmail.com',
    'url': 'https://github.com/JnyJny/twod.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
