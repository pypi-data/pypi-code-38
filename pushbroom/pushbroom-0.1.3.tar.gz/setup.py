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
    'version': '0.1.3',
    'description': 'Clean up your filesystem',
    'long_description': "# Pushbroom\n\nPushbroom is a tool designed to help keep your filesystem clear of clutter.\nCertain directories, such as your downloads directory, tend to accumulate a\nlarge amount of old files that take up space. Over time, this clutter can\naccumulate to a significant amount of storage space. Pushbroom gives you an easy\nway to remove these old files.\n\nPushbroom is written in Python and should therefore work on any platform that\ncan run Python. For now, it is only officially supported for macOS and Linux.\n\n## Installation\n\n### Homebrew (macOS only)\n\nInstall via Homebrew:\n\n    brew install gpanders/tap/pushbroom\n\nCopy and modify the included `pushbroom.conf` file to\n`~/.config/pushbroom/config` and use `brew services start\ngpanders/tap/pushbroom` to start the automatic launchd daemon:\n\n    cp -n /usr/local/etc/pushbroom.conf ~/.config/pushbroom/config\n    brew services start gpanders/tap/pushbroom\n\nPushbroom will run once every hour.\n\n### PyPI\n\nInstall using pip:\n\n    pip install pushbroom\n\n### From source\n\nCheck the [releases](https://github.com/gpanders/pushbroom/releases) page for\nthe latest release. Extract the archive and copy the files to their correct\nlocations:\n\n    tar xzf pushbroom-vX.Y.Z.tar.gz\n    cd pushbroom-vX.Y.Z\n    cp -r bin /usr/local/\n    cp -n pushbroom.conf ~/.config/pushbroom/config\n\n## Configuration\n\nThe Pushbroom configuration file is organized into sections where each section\nrepresents a directory path to monitor. The default configuration file looks\nlike this:\n\n    [Downloads]\n    Path = ~/Downloads\n    Trash = ~/.Trash\n    NumDays = 30\n\nThis means that, by default, Pushbroom will monitor your ~/Downloads folder and\nmove any file or folder older than 30 days into your ~/.Trash directory.\n\nIf you don't want to move files into ~/.Trash but instead want to just delete\nthem, simply remove the `Trash` option:\n\n    [Downloads]\n    Path = ~/Downloads\n    NumDays = 30\n\nThe name of the section (`Downloads` in this example) is not important and can\nbe anything you want:\n\n    [Home Directory]\n    Path = ~\n    NumDays = 90\n\nYou can also specify an `Ignore` parameter to instruct Pushbroom to ignore any\nfiles or directories that match the given glob:\n\n    [Downloads]\n    Path = ~/Downloads\n    NumDays = 30\n    Ignore = folder_to_keep/**/*\n\nThe following configuration items are recognized in `pushbroom.conf`:\n\n**Path**\n\nSpecify which directory to monitor\n\n**Trash**\n\nSpecify where to move files after deletion. If this option is not provided,\nfiles will simply be deleted.\n\n**NumDays**\n\nNumber of days to keep files in `Path` before they are removed.\n\n**Ignore**\n\nGlob expression pattern of files or directories to ignore.\n\n## Similar Work\n\n- [Belvedere](https://github.com/mshorts/belvedere): An automated file manager\n  for Windows\n- [Hazel](https://www.noodlesoft.com/): Automated Organization for your Mac\n",
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
