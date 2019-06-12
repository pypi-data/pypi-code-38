# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reading_helper']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['make_paper_page = '
                     'reading_helper:scripts_api.make_paper_page']}

setup_kwargs = {
    'name': 'reading-helper',
    'version': '0.1.5',
    'description': '',
    'long_description': '# reading-helper\n',
    'author': 'Nathan Hunt',
    'author_email': 'neighthan.hunt@gmail.com',
    'url': 'https://github.com/neighthan/reading-helper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
