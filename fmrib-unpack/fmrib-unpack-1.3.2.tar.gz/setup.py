#!/usr/bin/env python

import os.path as op

from setuptools import setup, find_packages


basedir = op.dirname(__file__)


with open(op.join(basedir, 'requirements.txt'), 'rt') as f:
    install_requires = [line.strip() for line in f.readlines()]
    install_requires = [line for line in install_requires if line != '']


with open(op.join(basedir, 'requirements-demo.txt'), 'rt') as f:
    demo_requires = [line.strip() for line in f.readlines()]
    demo_requires = [line for line in demo_requires if line != '']


with open(op.join(basedir, 'requirements-test.txt'), 'rt') as f:
    test_requires = [line.strip() for line in f.readlines()]
    test_requires = [line for line in demo_requires if line != '']


extras_require = {
    'demo' : demo_requires,
    'test' : test_requires
}


version = {}
with open(op.join(basedir, 'funpack', '__init__.py')) as f:
    for line in f:
        if line.startswith('__version__ = '):
            exec(line, version)
            break
version = version['__version__']


with open(op.join(basedir, 'README.rst'), 'rt') as f:
    readme = f.read()


setup(
    name='fmrib-unpack',
    version=version,
    description='The FMRIB UKBiobank Normalisation, Parsing '
                'And Cleaning Kit',
    long_description=readme,
    url='https://git.fmrib.ox.ac.uk/fsl/funpack',
    author='Paul McCarthy',
    author_email='pauldmccarthy@gmail.com',
    license='Apache License Version 2.0',

    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts' : [
            'funpack      = funpack.main:main',
            'funpack_demo = funpack.scripts.demo:main',
        ]
    }
)
