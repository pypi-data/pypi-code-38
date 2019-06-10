# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='asgi2gulp',
    version='0.1.5',
    description='Amorphous Structure Generator Interface to GULP',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Wojciech Szczypka',
    url='https://github.com/ws-qcnssp/asgi2gulp',
    license=license,
    py_modules=['asgi2gulp']
)