# -*- coding: utf-8 -*-

# Learn more: https://github.com/fillet54/qroutes

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()
    print readme

setup(
    name='qroutes',
    version='0.1.0',
    description='Compojure/Ring like WSGI library',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Phillip Gomez',
    author_email='fillet54@gmail.com',
    url='https://github.com/fillet54/qroutes',
    license="MIT License",
    packages=find_packages(exclude=('tests', 'docs'))
)

