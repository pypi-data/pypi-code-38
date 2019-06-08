############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
from setuptools import setup
# external packages
# local imports
from mountcontrol.mount import Mount


setup(
    name='mountcontrol',
    version=Mount.version,
    packages=[
        'mountcontrol',
        'mountcontrol.test',
    ],
    python_requires='>=3.7.2',
    install_requires=[
        'PyQt5>=5.12',
        'numpy>=1.16.2',
        'skyfield>=1.10',
    ],
    url='https://github.com/mworion/mountcontrol',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)
