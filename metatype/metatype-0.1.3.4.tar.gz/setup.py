# Copyright (c) 2018 WeFindX Foundation, CLG.
# All Rights Reserved.

from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='metatype',
    version='0.1.3.4',
    description='Implementation of base dict types for metaformat versions.',
    long_description=long_description,
    url='https://github.com/wefindx/metatype',
    author='Mindey',
    author_email='mindey@qq.com',
    license='MIT',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'metawiki',
        'typology',
        'gpgrecord',
        'python-dateutil',
    ],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False,
    entry_points = {
        'console_scripts': [
        ],
    }
)
