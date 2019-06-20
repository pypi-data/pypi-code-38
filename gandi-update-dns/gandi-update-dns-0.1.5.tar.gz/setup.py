# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gandi_update_dns']

package_data = \
{'': ['*']}

install_requires = \
['xdg>=3.0,<4.0']

extras_require = \
{'send-sms': ['send-sms-freemobile>=0.1.0,<0.2.0']}

entry_points = \
{'console_scripts': ['gandi-update-dns = gandi_update_dns:main']}

setup_kwargs = {
    'name': 'gandi-update-dns',
    'version': '0.1.5',
    'description': 'Yet another tool to update DNS zone in gandi provider',
    'long_description': 'Yet another tool to update DNS zone in Gandi provider!\n\n[![PyPI](https://img.shields.io/pypi/v/gandi-update-dns.svg)](https://pypi.org/project/gandi-update-dns/)\n[![PyPI - Status](https://img.shields.io/pypi/status/gandi-update-dns.svg)](https://pypi.org/project/gandi-update-dns/)\n[![PyPI - License](https://img.shields.io/pypi/l/gandi-update-dns.svg)](https://opensource.org/licenses/ISC)\n\n## How to use\n\nJust use the following command:\n\n    gandi-update-dns\n    \nIf the command is not on your PATH, it will be usually found on `$HOME/.local/bin`.\n\n## Configuration file\n\nIf you have no configuration file, the main command will ask you for a domain and a Gandi api key.\n\nConfiguration file can be found here:\n\n- Directory: XDG_CONFIG_HOME (default is `$HOME/.config`)\n- File: `gandi-update-dns.conf`\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/gandi-update-dns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
