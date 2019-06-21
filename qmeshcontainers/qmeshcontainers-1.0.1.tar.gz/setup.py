#!/usr/bin/env python
#
#    Copyright (C) 2018 Alexandros Avdis and others.
#    See the AUTHORS.md file for a full list of copyright holders.
#
#    This file is part of qmesh-containers.
#
#    qmesh-containers is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    qmesh-containers is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with qmesh-containers.  If not, see <http://www.gnu.org/licenses/>.
'''Set-up script for installation and packaging of setuptools-qmesh.

The aim of qmesh-containers is to facilitate testing, development and
distribution of qmesh, though Docker containers. The package source code
includes dockerfiles that build images used in testing and developing qmesh.
This script will install a command line utility that facilitates use of qmesh
images. The command-line utility fetches a base image and builds a second
image, tailored to the user.
'''

from setuptools import setup

def read(fname):
    '''Function reading file content.

    Function storing, and returning, file content as a string. Intended for reading the file
    containing the Version number and the read-me file during installation and packaging.

    Args:
        filename (str): Name of file to open and read contents.

    Returns:
        The file contents as a string (str).
    '''
    import os
    return open(os.path.join(os.path.dirname(__file__), fname), 'r').read().strip()

setup(
    name='qmeshcontainers',
    version=read('VERSION'),
    description="Create Docker container for using and developing qmesh",
    long_description=read('README.rst'),
    author="The qmesh development team.",
    author_email="develop@qmesh.org",
    url="https://www.qmesh.org",
    download_url=\
        'https://bitbucket.org/qmesh-developers/qmesh-containers/commits/tag/v'+\
        read('VERSION'),
    packages=['qmeshcontainers'],
    package_dir={'qmeshcontainers':'qmeshcontainers'},
    scripts=["qmeshcontainers/qmeshcontainer"],
    license='GPLv3',
    test_suite="tests",
    tests_require=['pylint', 'pyenchant'],
    keywords=['GIS', 'mesh generation', 'Docker'],
    package_data={'qmeshcontainers':['container_bashrc', '05-qmesh-container-welcome']})
