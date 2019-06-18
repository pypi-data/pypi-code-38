# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['idle_time']

package_data = \
{'': ['*']}

install_requires = \
['Jeepney>=0.4.0,<0.5.0']

extras_require = \
{':sys_platform == "windows"': ['pywin32>=224.0,<225.0']}

setup_kwargs = {
    'name': 'idle-time',
    'version': '0.1.0',
    'description': 'Detect user idle time',
    'long_description': '# idle-time\n\n[![pypi](https://img.shields.io/pypi/v/idle-time.svg)](https://pypi.python.org/pypi/idle-time) [![Build Status](https://travis-ci.org/escaped/idle-time.png?branch=master)](http://travis-ci.org/escaped/idle-time) [![Coverage](https://coveralls.io/repos/escaped/idle-time/badge.png?branch=master)](https://coveralls.io/r/escaped/idle-time) ![python version](https://img.shields.io/pypi/pyversions/idle-time.svg) ![Project status](https://img.shields.io/pypi/status/idle-time.svg) ![license](https://img.shields.io/pypi/l/idle-time.svg)\n\nDetect user idle time or inactivity on Linux and Windows.\n\n**WARNING** This project is in an alpha status! Though there is already some code to support Windows, it has only been tested on Wayland/Gnome. \n\n\n## Requirements\n\n* Python 3.6 or later\n\n\n## Installation\n\nInstall using `pip install idle-time`\n\n\n## Usage\n\nYou can use this module from the command line\n\n    python -m idle-time\n\nor access the current idle time from within your python program\n\n\n    from idle_time import IdleMonitor\n\n    monitor = IdleMonitor.get_monitor()\n    monitor.get_idle_time()\n',
    'author': 'Alexander Frenzel',
    'author_email': 'alex@relatedworks.com',
    'url': 'https://github.com/escaped/idle_time',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
