# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup, find_packages


REQUIRED_PACKAGES = [
    'deap==1.2.2'
]


with open('version.cache', 'r') as f:
    version = f.read()


setup(
    name="copter",
    version=version,
    packages=find_packages(),
    description='welcome to copter',
    platforms='Linux, Darwin',
    zip_safe=False,
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ]
)
