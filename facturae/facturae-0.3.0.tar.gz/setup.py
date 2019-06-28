# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from facturae import __version__

with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES = f.readlines()

with open('requirements-dev.txt', 'r') as f:
    TESTS_REQUIRES = f.readlines()

setup(
    name='facturae',
    version=__version__,
    url='http://www.gisce.net',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    original_author='Electrica Sollerense, S.A.U.',
    original_author_email='informatica@el-gas.es',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    license='GPLv3',
    description='Facturae',
    long_description=open('README.md').read(),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
