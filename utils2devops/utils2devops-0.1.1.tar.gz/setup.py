#!/usr/bin/env python

import os
from setuptools import setup, find_packages

from utils2devops.tools.description import get_long_description_from_file
from utils2devops.tools.single_sourcing_package_version import get_version

# doc is here
# https://setuptools.readthedocs.io/en/latest/setuptools.html#installing-setuptools

path = os.path.dirname(os.path.abspath(__file__))
long_description = get_long_description_from_file(path, 'README.rst')


setup(
    name='utils2devops',
    version=get_version('docs'),
    author='Alain IVARS',
    url='http://github.com/alainivars/utils2devops',
    author_email='alainivars@gmail.com',
    license='Apache License 2.0',
    description='''
    contain python 3 functions and class that can be helpfull in the all 
    working day
    ''',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    keywords='''
    Devops Docker Kubernete Terraform Lxd Lxc Aws
    ''',
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'boto3',  # AWS
        # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-init.html
        'aws-sam-cli',  # AWS
        'pylxd',  # LXD
    ]
)