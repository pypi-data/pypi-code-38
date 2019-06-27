# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tabbyj']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'ujson>=1.35,<2.0']

entry_points = \
{'console_scripts': ['tabbyj = tabbyj.__main__:tabbyj']}

setup_kwargs = {
    'name': 'tabbyj',
    'version': '0.2.2',
    'description': 'A command line JSON flattener',
    'long_description': '# tabbyj\n\nmeowj & catj, but in Python.\n\n## Installation\n\n### Via Pip (Recommended)\n\n```bash\npython -m pip install tabbyj\n```\n\n### From source (For development)\n\n1. Install [Poetry](https://poetry.eustace.io/)\n2. `git clone https://github.com/nint8835/tabbyj.git`\n3. `cd tabbyj`\n4. `poetry install`\n\nPlease note that this will create a virtualenv and install the package into it. If you wish to use the package globally, please install it via Pip.\n\n## Usage\n\n### Piping\n\nTabbyj allows the user to simply pipe data into it in order to process it. For example:\n\n```bash\ncurl https://api.github.com/gists | tabbyj\n```\n\n### Reading from a file\n\nTabbyj allows the user to easily read the data to process from a file via a command line argument. For example:\n\n```bash\ntabbyj --file example.json\n```\n',
    'author': 'Riley Flynn',
    'author_email': 'riley@rileyflynn.me',
    'url': 'https://github.com/nint8835/tabbyj',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
