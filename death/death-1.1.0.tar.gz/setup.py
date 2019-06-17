#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
setup(name='death',
      version='1.1.0',
      description='Dapth is a simple argument parser tool to get the cmdline argumets',
      long_description=readme(),
      url='http://github.com/HeeroYui/death',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='MPL-2',
      packages=['death'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='log logs debug print console',
      include_package_data = True,
      zip_safe=False)

#To developp: sudo ./setup.py install
#             sudo ./setup.py develop
#pylint test: pylint2 --rcfile=pylintRcFile.txt death/debug.py

#TO register all in pip: use external tools:
#  pip install twine
#  # create the archive
#  ./setup.py sdist
#  twine upload dist/*

