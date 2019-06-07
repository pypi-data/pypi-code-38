# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['polyanalyst6api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.19,<3.0']

setup_kwargs = {
    'name': 'polyanalyst6api',
    'version': '0.5.0',
    'description': 'polyanalyst6api is a PolyAnalyst API client for Python.',
    'long_description': None,
    'author': 'yatmanov',
    'author_email': 'yatmanov@megaputer.ru',
    'url': 'https://github.com/Megaputer/polyanalyst6api-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
