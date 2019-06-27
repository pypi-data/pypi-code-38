# -*- coding: utf-8 -*-
"""
A library created by Cofense Intelligence to support developing integregations with client security architecture.

For more information on gaining access to Cofense Intelligence data at
https://cofense.com/product-services/phishing-intelligence

If you are already a customer, detailed documentation on the Intelligence API can be found at
https://www.threathq.com/docs/

The download and/or use of this Cofense application is subject to the terms and conditions set forth at https://cofense.com/legal/integration-applications/.

Copyright 2013-2018 Cofense, Inc.  All rights reserved.

This software is provided by Cofense, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.

Author: Cofense Intelligence Solutions Engineering
Support: support@cofense.com
"""

from os import path
from setuptools import setup, find_packages

from cofense_intelligence import __version__

package_path = path.abspath(path.dirname(__file__))

setup(
    name='cofense_intelligence',
    version=__version__,
    url='https://www.threathq.com/docs/',
    license='Proprietary',
    description='Cofense Intelligence Integration Library',
    long_description=__doc__,
    author='Cofense Intelligence Solutions Engineering',
    author_email='support@cofense.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: Free To Use But Restricted',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
    ],
    keywords='phishing threat intelligence cofense intelligence',
    install_requires=['requests>=2.3', 'defusedxml>=0.5.0', 'six>=1.11.0', 'jinja2>=2.10'],
    packages=find_packages(),
    entry_points={'console_scripts': [
        'cofense-intelligence = cofense_intelligence.cli:execute',
    ]},
    include_package_data=True,
)
