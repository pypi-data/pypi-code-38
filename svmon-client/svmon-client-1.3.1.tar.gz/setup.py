#!/usr/bin/python
# -*- coding: UTF-8 -*-


from setuptools import setup, find_packages


setup( 
name='svmon-client',
version='1.3.1',
packages=['svmon_client'],
scripts=['svmon','pakiti-client'],
package_data={'' : ['*.json','*.pem']},
description='This is a python implementation of SVMON client',
long_description=open('README.rst').read(), 
author='Jie Yuan',
author_email='jie.yuan@kit.edu',
maintainer='Jie Yuan',
maintainer_email='jie.yuan@kit.edu',
license='MIT License',
platforms=["all"],
url='https://gitlab.eudat.eu/jie.yuan/pysvmon',
classifiers=[ 
    'Development Status :: 4 - Beta', 
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries' ]
)
