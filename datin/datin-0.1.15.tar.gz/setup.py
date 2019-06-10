# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, Extension, find_packages


with open('/Users/RT/projects/datin/README.rst') as f:
    readme = f.read()

setup(
    name='datin',
    version='0.1.15',
    description='Convert data into columnar format',
    long_description="this is a long description of the module",
    long_description_content_type="text/plain",
    author='Ryan Trigg',
    author_email='rbutustree@gmail.com',
    url='https://github.com/rbutus/datin.git',
    license="MIT License",
    packages=find_packages(),
    install_requires=['pandas', 'numpy'],
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
    ],
)

