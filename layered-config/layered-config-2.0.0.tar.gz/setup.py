# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['layered_config']

package_data = \
{'': ['*']}

extras_require = \
{'munch': ['munch']}

setup_kwargs = {
    'name': 'layered-config',
    'version': '2.0.0',
    'description': 'A tool for managing layered config files!',
    'long_description': None,
    'author': 'Ryan Casperson',
    'author_email': 'casperson.ryan@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
