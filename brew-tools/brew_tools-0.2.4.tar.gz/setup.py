# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['brew_tools']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['brew_tools = brew_tools.command_line:run']}

setup_kwargs = {
    'name': 'brew-tools',
    'version': '0.2.4',
    'description': 'Commandline tools for the homebrewer',
    'long_description': 'brew-tools\n==========\n\n::\n\n    ╔╗ ╦═╗╔═╗╦ ╦  ╔╦╗╔═╗╔═╗╦  ╔═╗\n    ╠╩╗╠╦╝║╣ ║║║───║ ║ ║║ ║║  ╚═╗\n    ╚═╝╩╚═╚═╝╚╩╝   ╩ ╚═╝╚═╝╩═╝╚═╝\n\n|Build Status| |Documentation Status| |PyPI version|\n\nA command line utility that offers a set of calculators for home\nbrewers.\n\n    NOTE: All values and calculations are provided as guidelines only.\n    Brew-tools should not be used for professional brewing. No warranty\n    or guarantee of accuracy is provided on the information provided by\n    this calculator.\n\nDescription\n===========\n\nNeed to do a quick calculation during your brew day? Don\'t fancy digging\nthrough a GUI application, or a web based tool? Prefer to do simple\nthings in a terminal?\n\nThen **brew-tools** is for you.\n\nCurrently brew-tools includes:\n\n-  ABV calculator\n-  Keg priming calculator\n-  Priming sugar calculator\n-  Quick infusion calculator\n-  Adjust gravity with dme calculator\n-  Apparent and Real attenuation calculator\n-  Final gravity from a given attenuation percentage\n-  Gravity adjustment by boil off/dilution calculator\n-  New gravity after volume adjustment\n\nMore to come\n\nSee the `changelog <CHANGELOG.rst>`__ for updates in each version\n\nInstallation\n============\n\nBrew-tools is available from PyPI\n\n::\n\n    pip install brew-tools\n\nYou can also clone/download this repository and install it using pip\n\n::\n\n    cd <brew-tools-dir>\n    pip install .\n\nUsage\n=====\n\nBrew tools has built in help\n\n::\n\n    Usage: brew-tools [OPTIONS] COMMAND [ARGS]...\n\n    Options:\n    --version  Show the version and exit.\n    -imperial  Use imperial units. Metric by default.\n    --help     Show this message and exit.\n\n    Commands:\n    abv\n    infuse\n    kegpsi\n    prime\n    dme\n\nand also for its commands\n\n::\n\n    brew-tools infuse --help\n    Usage: brew-tools infuse [OPTIONS]\n\n    Options:\n      -temp FLOAT    Current temperature of mash\n      -target FLOAT  Target temperature of mash\n      -ratio FLOAT   Grist/water ratio\n      -grain FLOAT   Weight of grain in mash\n      -water FLOAT   Temp of infusion water\n      --help         Show this message and exit.\n\nIf the inputs are not passed via the command line arguments, brew tools\nwill prompt the user for input.\n\nFor more information see the\n`documentation <https://brew-tools.readthedocs.io/en/latest/>`__\n\nDevelopment\n===========\n\nIf you want to help develop brew tools you should install it into a\nvirtual environment.\n\nCreate and source the environment and then install brew tools with\n\n::\n\n    cd <brew-tools project dir>\n    pip install -e ".[testing]"\n\nwhich will install an editable version, as well as all the tools\nrequired to run the tests with\n\n::\n\n    pytest tests\n\nIn addition to the tests it\'s advisable to run a linter of the source as\nTravis will also check for linting errors. The linter command ignores\nsome errors, so you can use this command to match the command run by\nTravis\n\n::\n\n    flake8 src --ignore=E501,W504,W503\n\nThanks\n======\n\nThanks to\n\n-  /u/DAMNIT\\_REZNO - for inspiring me to start this project\n-  SlayterDev - DME addition calculator\n\nLicense\n=======\n\nBrew Tools is released under the MIT license.\n\nSee ``LICENSE.txt`` for more details\n\n.. |Build Status| image:: https://travis-ci.com/Svenito/brew-tools.svg?branch=master\n   :target: https://travis-ci.com/Svenito/brew-tools\n.. |Documentation Status| image:: https://readthedocs.org/projects/brew-tools/badge/?version=latest\n   :target: https://brew-tools.readthedocs.io/en/latest/?badge=latest\n.. |PyPI version| image:: https://badge.fury.io/py/brew-tools.svg\n   :target: https://badge.fury.io/py/brew-tools\n',
    'author': 'Sven',
    'author_email': 'sven@unlogic.co.uk',
    'url': 'https://github.com/Svenito/brew-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
