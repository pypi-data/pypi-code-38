# -*- coding: utf-8 -*-
'''
Copyright 2019 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Filename: setup.py
Created Date: 2019-05-06
Author: Jacques Supcik
'''

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()  # pylint: disable=invalid-name

setup(
    name='pvfr.groopledb',
    description='Package to read data from the Groople MySQL Database',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jacques Supcik',
    author_email='jacques@pvfr.ch',
    url='https://github.com/passeport-vacances/groopledb',
    packages=['pvfr.groopledb'],
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'PyMySQL',
        'records',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
