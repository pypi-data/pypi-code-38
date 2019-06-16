#!/usr/bin/env python3

import sys
import setuptools
import os
from distutils.core import setup
from rabbitholer.version import __version__


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


if sys.version_info < (3, 3):
    print("THIS MODULE REQUIRES PYTHON 3.3+. YOU ARE CURRENTLY\
    USING PYTHON {0}".format(sys.version))
    sys.exit(1)

setup(
    name="rabbitholer",
    version=__version__,
    include_package_data=True,
    author="Stanislav Arnaudov",
    author_email="stanislv_ts@abv.bg",
    description="A simple tool to send and receive messages to and from rabbitmq\
exchanges and queues",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="GNU General Public License v3.0",
    keywords="rabbitmq sender receiver",
    url="https://github.com/palikar/rabbitholer",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [
            'rabbitholer = rabbitholer.main:main'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
