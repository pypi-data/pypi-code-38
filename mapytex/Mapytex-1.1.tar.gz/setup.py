#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Mapytex',
    version='1.1',
    description='Computing like a student',
    author='Benjamin Bertrand',
    author_email='lafrite@poneyworld.net',
    packages=['mapytex'],
    # install_requires=['pyparsing', 'sympy'],
    )
