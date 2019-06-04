#!/usr/bin/env python
from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wafer-debconf',
    version='0.1.8',
    description='Wafer extensions used by DebConf',
    author='DebConf Team',
    author_email='debconf-team@lists.debian.org',
    url='https://salsa.debian.org/debconf-team/public/websites/wafer-debconf',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Conferencing',
    ],
)
