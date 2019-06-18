# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pushbroom']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pushbroom = pushbroom.console:run']}

setup_kwargs = {
    'name': 'pushbroom',
    'version': '0.1.2',
    'description': 'Clean up your filesystem',
    'long_description': '# Pushbroom\nKeep select filesystem paths free of clutter\n\n## Installation\n\nInstall via Homebrew:\n\n    brew install gpanders/tap/pushbroom\n\nOr directly from source (requires [poetry](https://github.com/sdispater/poetry)):\n\n    git clone https://github.com/gpanders/pushbroom\n    cd pushbroom\n    poetry install\n\nOr from PyPI:\n\n    pip install pushbroom\n\nPushbroom comes with an example configuration file `pushbroom.conf`. You can\ncopy this to either `$XDG_CONFIG_HOME/pushbroom/config` or `$HOME/.pushbroomrc` and\nmodify it to your needs.\n\n## Configuration\n\nThe following configuration items are recognized in `pushbroom.conf`:\n\n**Path**\n\nSpecify which directory to monitor\n\n**Trash**\n\nSpecify where to move files after deletion. If this option is not provided,\nfiles will simply be deleted.\n\n**NumDays**\n\nNumber of days to keep files in `Path` before they are removed.\n\n**Ignore**\n\nRegular expression pattern of files or directories to ignore.\n',
    'author': 'Greg Anders',
    'author_email': 'greg@gpanders.com',
    'url': 'https://github.com/gpanders/pushbroom',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
