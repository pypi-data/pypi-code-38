# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='attr-descriptions',
    version='0.1.2',
    description='A mini-module that helps to add descriptions to attrs attributes.',
    long_description=readme,
    author='Deniz Bozyigit',
    author_email='deniz195@gmail.com',
    url='https://github.com/deniz195/attr-descriptions',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = ['attr', 'cattrs', 'pytest']
)
