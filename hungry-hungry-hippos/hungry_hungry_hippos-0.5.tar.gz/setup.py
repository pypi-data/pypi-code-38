# -*- coding: utf-8 -*-
#!/usr/bin/python

import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(name='hungry_hungry_hippos',
    version='0.5',
    description='A python implementation of redlock, with examples',
    long_description=long_description,
    long_description_content_type="text/markdown",      
    url='https://github.com/krezreb/hungryhungryhippos',
    author='krezreb',
    author_email='josephbeeson@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'redis',
    ],
    zip_safe=False)





