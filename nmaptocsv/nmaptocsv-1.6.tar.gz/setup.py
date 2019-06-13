#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='nmaptocsv',
      version='1.6',
      description='A simple python script to convert Nmap output to CSV',
      long_description_content_type='text/markdown; charset=UTF-8;',
      long_description=open('nmaptocsv/README.md').read(),
      url='https://github.com/maaaaz/nmaptocsv',
      author='Thomas D.',
      author_email='tdebize@mail.com',
      license='LGPL',
      classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7'
      ],
      keywords='nmap scan output csv gnmap xml',
      packages=find_packages(),
      install_requires=['argparse', 'future'],
      python_requires='>=2.7',
      entry_points = {
        'console_scripts': ['nmaptocsv=nmaptocsv.nmaptocsv:main'],
      },
      include_package_data=True)