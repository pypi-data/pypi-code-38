# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['organize', 'organize.actions', 'organize.filters']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'Send2Trash>=1.5,<2.0',
 'appdirs>=1.4,<2.0',
 'clint>=0.5.1,<0.6.0',
 'colorama>=0.4.1,<0.5.0',
 'docopt>=0.6.2,<0.7.0']

extras_require = \
{':python_version < "3.4"': ['pathlib2==2.3.0'],
 ':python_version < "3.5"': ['typing>=3.6,<4.0', 'pathlib2>=2.3.3,<3.0.0']}

entry_points = \
{'console_scripts': ['organize = organize.main:main']}

setup_kwargs = {
    'name': 'organize-tool',
    'version': '1.4.3',
    'description': 'The file management automation tool',
    'long_description': '.. image:: https://github.com/tfeldmann/organize/raw/master/docs/images/organize.svg?sanitize=true\n\n.. image:: https://readthedocs.org/projects/organize/badge/?version=latest\n  :target: https://organize.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n\n.. image:: https://travis-ci.org/tfeldmann/organize.svg?branch=master\n    :target: https://travis-ci.org/tfeldmann/organize\n\norganize\n========\n**The file management automation tool.**\n\nInstall via pip (requirement: Python 3.3+):\n\nOn macOS / Windows:\n``$ pip3 install organize-tool``\n\nOn Linux:\n``$ sudo pip3 install organize-tool``\n\n\nWhy you might find this useful\n------------------------------\nYour desktop is a mess? You cannot find anything in your downloads and\ndocuments? Sorting and renaming all these files by hand is too tedious?\nTime to automate it once and benefit from it forever.\n\n*organize* is a command line, open-source alternative to apps like Hazel (macOS)\nor File Juggler (Windows).\n\nIn your shell, run ``$ organize config`` to edit the configuration:\n\n- ``config.yaml``:\n\n  .. code-block:: yaml\n\n      rules:\n        # move screenshots into "Screenshots" folder\n        - folders:\n            - ~/Desktop\n          filters:\n            - Filename:\n                startswith: \'Screen Shot\'\n          actions:\n            - Move: ~/Desktop/Screenshots/\n\n        # move incomplete downloads older > 30 days into the trash\n        - folders:\n            - ~/Downloads\n          filters:\n            - Extension:\n                - download\n                - crdownload\n                - part\n            - LastModified:\n                days: 30\n                mode: older\n          actions:\n            - Trash\n\n(alternatively you can run ``$ organize config --path`` to see the full path to\nyour ``config.yaml``)\n\n``$ organize run`` will now...\n\n- move all your screenshots from your desktop a "Screenshots" subfolder\n  (the folder will be created if it does not exist)\n- put all incomplete downloads older than 30 days into the trash\n\nIt is that easy.\n\nFeeling insecure? Run ``$ organize sim`` to see what would happen without\ntouching your files.\n\nBut there is more. You want to rename / copy files, run custom shell- or python\nscripts, match filenames with regular expressions or use placeholder variables?\n`organize` has you covered.\n\nHave a look at the full documentation at https://organize.readthedocs.io/.\n\n\nAdvanced usage example\n----------------------\nThis example shows some advanced features like placeholder variables, pluggable\nactions and recursion through subfolders:\n\n.. code-block:: yaml\n\n    rules:\n      - folders: \'~/Documents\'\n        subfolders: true\n        filters:\n          - Extension:\n              - pdf\n              - docx\n          - LastModified\n        actions:\n          - Move: \'~/Documents/{extension.upper}/{lastmodified.year}/\'\n          - Shell: \'open "{path}"\'\n\nGiven we have two files in our ``~/Documents`` folder (or any of its subfolders)\nnamed ``script.docx`` from year 2018 and ``demo.pdf`` from year 2016 this will\nhappen:\n\n- ``script.docx`` will be moved to ``~/Documents/DOCX/2018/script.docx``\n- ``demo.pdf`` will be moved to ``~/Documents/PDF/2016/demo.pdf``\n- The files will be opened (``open`` command in macOS) from their new location.\n\n\nFunctionality\n-------------\n\n**Select files by** (filters):\n\n- Extension\n- Regular expression\n- Last modified date (newer, older)\n- Filename (startswith, endswith, contains)\n\n**Organize your files** (actions):\n\n- Move files\n- Copy files\n- Rename files in place\n- Run shell command\n- Run inline Python code\n- Move into Trash\n- Print something to the console\n\nIf you miss a feature please file an issue. Pull requests welcome!\n\n\nCommand line interface\n----------------------\n::\n\n  The file management automation tool.\n\n  Usage:\n      organize sim [--config-file=<path>]\n      organize run [--config-file=<path>]\n      organize config [--open-folder | --path | --debug] [--config-file=<path>]\n      organize list\n      organize --help\n      organize --version\n\n  Arguments:\n      sim             Simulate a run. Does not touch your files.\n      run             Organizes your files according to your rules.\n      config          Open the configuration file in $EDITOR.\n      list            List available filters and actions.\n      --version       Show program version and exit.\n      -h, --help      Show this screen and exit.\n\n  Options:\n      -o, --open-folder  Open the folder containing the configuration files.\n      -p, --path         Show the path to the configuration file.\n      -d, --debug        Debug your configuration file.\n\n  Full documentation: https://organize.readthedocs.io\n',
    'author': 'Thomas Feldmann',
    'author_email': 'mail@tfeldmann.de',
    'url': 'https://github.com/tfeldmann/organize',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
