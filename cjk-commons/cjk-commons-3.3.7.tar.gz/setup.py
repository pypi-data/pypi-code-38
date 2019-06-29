# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cjk_commons']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0', 'appdirs>=1.4,<2.0', 'yodl>=1.0,<2.0']

setup_kwargs = {
    'name': 'cjk-commons',
    'version': '3.3.7',
    'description': 'Commons',
    'long_description': None,
    'author': 'Cujoko',
    'author_email': 'cujoko@gmail.com',
    'url': 'https://github.com/Cujoko/commons',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
