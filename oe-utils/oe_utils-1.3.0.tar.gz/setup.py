# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()

requires = [
    'sqlalchemy',
    'requests',
    'PyYAML',
    'colander',
    'feedgen',
    'simplejson',
]

setup(
    name='oe_utils',
    version='1.3.0',
    description='Utility Library',
    long_description=README + '\n\n' + CHANGES,
    url='https://github.com/OnroerendErfgoed/oe_utils',
    author='Flanders Heritage Agency',
    author_email='ict@onroerenderfgoed.be',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='oe utility',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requires,
    entry_points={
    },
)
