#!/usr/bin/env python3

from setuptools import find_packages, setup

INSTALL_REQUIRES = ['numpy >= 1.14', 'matplotlib',
                    'pandas', 'scipy', 'scikit-learn',
                    'spectral_connectivity', 'hmmlearn']
TESTS_REQUIRE = ['pytest >= 2.7.1']

setup(
    name='spindle_detector',
    version='0.1.0.dev0',
    license='MIT',
    description=('Identify spindle events'),
    author='',
    author_email='',
    url='https://github.com/Eden-Kramer-Lab/spindle_detector',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
)
