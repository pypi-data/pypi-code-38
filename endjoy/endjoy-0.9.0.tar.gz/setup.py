# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['endjoy']
install_requires = \
['inotify>=0.2.10,<0.3.0']

entry_points = \
{'console_scripts': ['ej = endjoy:main', 'endjoy = endjoy:main']}

setup_kwargs = {
    'name': 'endjoy',
    'version': '0.9.0',
    'description': 'Ctrl-Z for the filesystem',
    'long_description': "# endjoy\n\n> Ctrl-Z for the filesystem\n\n## What is endjoy?\nEndjoy is a command line program that allows you to restore all the files in a directory to the state they were in some time ago. Therefore, it allows you to revert modifications, deletions and creations of the files in the watched directory.  \nWith this you can just try out any changes without fear, as you can always revert them with a single command.\n\n## Install\n```bash\nsudo pip install endjoy\n```\n\n## Usage\n\n```bash\nej start # Start recursively monitoring the working directory\n\n# Modify/create/delete some files or directories...\n\nej revert 5m # Revert changes done in the last five minutes\nej revert 1h # Revert changes done in the last hour\n\nej checkpoint NAME # Checkpoint the current state of the directory\nej checkpoint # List all the stored checkpoints\n\n# Modify some more files\n\nej revert NAME # Revert the directory to how it was when the checkpoint NAME was created\n\nej suicide # Stop monitoring the directory and delete all temporary files created\n```\n\n## What makes endjoy different from git?\n> tl;dr: endjoy is git stash on steroids\n\nThe most important difference between git and endjoy is that the latter runs in the background whereas git doesn't, this means that:\n- Doesn't require setting explicit checkpoints as with `git commit`\n- Runs asynchronously, so you don't have to wait for `git` to finish\n- Doesn't require any action till you need to use it to restore a previous state\n\nIf you need complex functionality, like merging different commits/checkpoints or moving forward and backwards between them, git is a better choice, as endjoy is much simpler and doesn't implement that\n\n## Why is it called endjoy?\n![See https://battleangel.fandom.com/wiki/Endjoy](https://raw.githubusercontent.com/corollari/endjoy/master/endjoy.png)\n\n## Development\nInstall from source (requires poetry):\n```bash\n# Optional\nvirtualenv --python=python3 venv\n. venv/bin/activate\n# Required\npoetry install\n# Run\nej\n# Run tests\npytest\n```\n\n## How does it work?\nOn `start` it spawns a process, that will act as the server, with two threads:\n- One thread subscribes to be notified of changes on all the directories especified via [inotify](http://man7.org/linux/man-pages/man7/inotify.7.html) and stores all the changes along with a timestamp in shared memory\n- Another thread creates a named pipe and listens on it, when endjoy is called again with another command this thread performs whatever command was issued using the data that has been gathered by the first thread (inotify one)\n\n## Authors\n[@luis136](https://github.com/luis136) and [@corollari](https://github.com/corollari)\n\n## License\n[The Unlicense](https://raw.githubusercontent.com/corollari/endjoy/master/LICENSE)\n",
    'author': 'Albert',
    'author_email': 'github@albert.sh',
    'url': 'https://github.com/corollari/endjoy',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
