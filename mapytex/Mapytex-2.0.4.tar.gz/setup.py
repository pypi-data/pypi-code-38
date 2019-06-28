#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Mapytex',
    version='2.0.4',
    description='Computing like a student',
    author='Benjamin Bertrand',
    author_email='programming@opytex.org',
    url='http://git.opytex.org/lafrite/Mapytex',
    packages=['mapytex'],
    include_package_data = True,
    install_requires=[
        'multipledispatch',
        'tabulate',
    ],
    )
