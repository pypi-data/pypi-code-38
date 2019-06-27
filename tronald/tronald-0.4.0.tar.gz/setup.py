# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tronald']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'inquirer>=2.5,<3.0', 'paramiko>=2.4,<3.0']

entry_points = \
{'console_scripts': ['tronald = tronald.__main__:cli']}

setup_kwargs = {
    'name': 'tronald',
    'version': '0.4.0',
    'description': 'CLI for getting Postgres dumps from remote containers.',
    'long_description': None,
    'author': 'Filip Weidemann',
    'author_email': 'filip.weidemann@outlook.de',
    'url': 'https://github.com/filipweidemann/tronald',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
