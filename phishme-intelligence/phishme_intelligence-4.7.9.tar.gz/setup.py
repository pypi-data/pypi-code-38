# -*- coding: utf-8 -*-
"""
A library created by PhishMe Intelligence to support developing integregations with client security architecture.

For more information on gaining access to PhishMe Intelligence data at
https://phishme.com/product-services/phishing-intelligence

If you are already a customer, detailed documentation on the Intelligence API can be found at
https://www.threathq.com/documentation/display/MAD

The download and/or use of this PhishMe application is subject to the terms and conditions set forth at https://phishme.com/legal/integration-applications/.

Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

Author: PhishMe Intelligence Solutions Engineering
Support: support@phishme.com
"""

from os import path
from setuptools import setup, find_packages

from phishme_intelligence import __version__

package_path = path.abspath(path.dirname(__file__))

setup(
    name='phishme_intelligence',
    version=__version__,
    url='https://www.threathq.com/documentation/display/MAD',
    license='Proprietary',
    description='PhishMe Intelligence Integration Library',
    long_description=__doc__,
    author='PhishMe Intelligence Solutions Engineering',
    author_email='support@phishme.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: Free To Use But Restricted',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Security',
    ],
    keywords='phishing threat intelligence',
    install_requires=['requests>=2.3', 'defusedxml>=0.5.0', 'six>=1.11.0'],
    packages=find_packages(),
    include_package_data=True
)
