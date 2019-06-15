# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['trustpilotreviews']

package_data = \
{'': ['*']}

install_requires = \
['dataset>=1.1,<2.0',
 'numpy>=1.15,<2.0',
 'pandas>=0.23.0,<0.24.0',
 'requests>=2.20,<3.0',
 'stuf>=0.9.16,<0.10.0']

setup_kwargs = {
    'name': 'trustpilotreviews',
    'version': '0.1.0',
    'description': 'Unoffice TrustPilot API to download reviews scores and contents',
    'long_description': None,
    'author': 'Prayson Wilfred Daniel',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
