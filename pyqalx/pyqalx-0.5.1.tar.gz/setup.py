# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyqalx',
 'pyqalx.bot',
 'pyqalx.config',
 'pyqalx.config.defaults',
 'pyqalx.core',
 'pyqalx.core.entities',
 'pyqalx.transport',
 'pyqalx.vendor',
 'qalxcli']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9.153,<2.0.0',
 'click>=7.0,<8.0',
 'dill>=0.2.9,<0.3.0',
 'jsonschema>=3.0,<4.0',
 'requests>=2.21,<3.0']

extras_require = \
{'sphinx': ['sphinx>=2.0,<3.0']}

entry_points = \
{'console_scripts': ['qalx = qalxcli.__init__:qalx']}

setup_kwargs = {
    'name': 'pyqalx',
    'version': '0.5.1',
    'description': 'High-level interfaces to the qalx API',
    'long_description': 'pyqalx\n======\n\nInterfaces to qalx. For more details, see `project documentation, <http://docs.qalx.io>`_.\n\n.. admonition:: development status\n\n   ``pyqalx`` is currently under active development. It is pre-version 1.0 beta software and so each minor version\n   can introduce breaking changes.\n\n**qalx** (an abbreviation of "queued calculations" and pronounced "kal-x") is a flexible data management platform for engineering projects. Users store data and files in qalx and it provides tools for passing that data between various systems for processing.\n\nThere will eventually be four ways to interact with the platform:\n\n-  A Python interface (pyqalx)\n-  REST API (api.qalx.io)\n-  Web console (qalx.io) - coming soon\n-  A command line interface (qalx-cli) - coming soon\n\nMost users are expected to use the web console and either the python or\ncommand line interfaces. The REST API is intended to be used if you\nprefer to access the platform with a language other than Python or want\nto create a custom interface.\n\n.. _installing:\n\nInstalling\n==========\n\n**qalx** is written in `Python <https://python.org>`_ and can be\ninstalled via the Python Package Index (PyPi) with:\n\n.. code:: bash\n\n   pip install pyqalx\n\nIf installation has completed properly you should be able to import\n``pyqalx`` in a python console:\n\n>>> import pyqalx\n\n.. warning::\n\n      pyqalx requires **Python versions above 3.6**.\n\n\nConfiguration and Authentication\n--------------------------------\n\nEverything you do with **qalx** requires you to be authenticated. That\nis, the platform requires you to identify yourself and will record all\nyour actions as being performed by you.\n\nThe way that **qalx** knows who you are is by reading a ``TOKEN``\nwhich must be sent with every request.\n\n.. warning::\n   During this beta phase, you have to request a ``TOKEN`` by registering your interest at `qalx.io <https://qalx.io>`_\n\nThe easiest way to make sure that your token is sent with every request is to make sure you have a valid ``.qalx`` file\nsaved in your HOME directory.\n\n.. admonition::  where is ``HOME``?\n\n   The ``HOME`` directory can usually be found by putting %USERPROFILE%\n   in the address bar in Windows Explorer or it is simply ``~`` on unix\n   systems.\n\nAdding the ``TOKEN`` to your config file under the default profile will ensure automatic\nauthentication.\n\n.. code:: ini\n\n   [default]\n   TOKEN = 632gd7yb9squd0q8sdhq0s8diqsd0nqsdq9sdj\n\nAny other configuration settings can be stored in the same file see `<https://docs.qalx.io/configuration>`_ for more information.\n\nQuickstart\n----------\n\nThe best place to get started: `<https://docs.qalx.io/quickstart>`_\n\n\n\n',
    'author': 'AgileTek Engineering Limited',
    'author_email': 'london@agiletek.co.uk',
    'url': 'https://qalx.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
