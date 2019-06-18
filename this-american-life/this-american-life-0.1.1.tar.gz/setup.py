#!/usr/bin/env python
from os import path
from setuptools import setup, find_packages


package_name = 'this-american-life'
tal_module_ref = __import__(package_name.replace('-', ''))

# read the README
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=package_name,
    version=tal_module_ref.__version__,
    description='scraper client for the This American Life website',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email=tal_module_ref.__author_email__,
    url='https://github.com/{package_name}',
    packages=find_packages(exclude=['tests']),
    install_requires=['lxml', 'requests'],
    python_requires='>=3.6.0'
)
