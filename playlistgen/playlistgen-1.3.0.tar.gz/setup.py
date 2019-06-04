# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['playlistgen']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'lxml>=4.3,<5.0', 'moviepy>=1.0,<2.0']

entry_points = \
{'console_scripts': ['genlist = playlistgen.playlist:generate']}

setup_kwargs = {
    'name': 'playlistgen',
    'version': '1.3.0',
    'description': 'Hobby project to generate vlc playlists',
    'long_description': None,
    'author': 'Arslan',
    'author_email': 'rslnkrmt2552@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
