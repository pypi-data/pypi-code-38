# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['zokrates_pycrypto', 'zokrates_pycrypto.gadgets']

package_data = \
{'': ['*']}

install_requires = \
['bitstring>=3.1,<4.0']

setup_kwargs = {
    'name': 'zokrates-pycrypto',
    'version': '0.2.0',
    'description': 'Accompanying crypto application code for the zkSNARKs toolbox ZoKrates',
    'long_description': None,
    'author': 'sdeml',
    'author_email': 'stefandeml@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
