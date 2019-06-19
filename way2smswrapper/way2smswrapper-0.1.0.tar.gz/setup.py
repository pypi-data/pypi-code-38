# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['way2smswrapper']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=3.141,<4.0', 'xvfbwrapper>=0.2.9,<0.3.0']

setup_kwargs = {
    'name': 'way2smswrapper',
    'version': '0.1.0',
    'description': 'A Python Messaging Module Using Way2SMS & Selenium Module.',
    'long_description': None,
    'author': 'Probhakar Roy',
    'author_email': 'probhakarroy3110@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
