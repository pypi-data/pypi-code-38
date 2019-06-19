# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['carly']

package_data = \
{'': ['*']}

install_requires = \
['Twisted>=18', 'attrs']

setup_kwargs = {
    'name': 'carly',
    'version': '0.10.2',
    'description': 'A tool for putting messages into and collecting responses from Twisted servers using real networking',
    'long_description': 'carly\n=====\n\n|CircleCI|_\n\n.. |CircleCI| image:: https://circleci.com/gh/cjw296/carly/tree/master.svg?style=shield\n.. _CircleCI: https://circleci.com/gh/cjw296/carly/tree/master\n\n\nA tool for putting messages into and collecting responses from Twisted servers and clients using real networking.\n\n"call me maybe"\n\nWhy carly? \'cos someone already took `Jepsen!`__\n\n__ https://jepsen.io/\n',
    'author': 'Chris Withers',
    'author_email': 'chris@withers.org',
    'url': 'https://github.com/cjw296/carly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
