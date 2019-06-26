#!/usr/bin/env python

from setuptools import setup

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

__author__ = 'Jason Corbett'


def get_requirements(filename):
    with open(filename) as f:
        return f.readlines()

setup(
    name="slickqa-snot",
    description="A plugin to nose to allow results from python tests to be put into slick.",
    version="1.0.2949",
    license="License :: OSI Approved :: Apache Software License",
    long_description=open('README.md').read(),
    py_modules=['snot'],
    # packages=find_packages(exclude=['distribute_setup']),
    # package_data={'': ['*.txt', '*.rst', '*.html']},
    # include_package_data=True,
    install_requires=get_requirements('requirements.txt'),
    author="Slick Developers",
    url="http://github.com/slickqa/snot",
    entry_points={
        'nose.plugins.0.10': [
            'snot = snot:SlickAsSnotPlugin'
        ]
    }
)
