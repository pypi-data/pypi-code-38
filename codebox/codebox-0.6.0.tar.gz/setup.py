"""codebox package setup"""
from os import path
from codecs import open
from setuptools import setup, find_packages

THIS_FOLDER = path.abspath(path.dirname(__file__))

# Get package version from .version file
with open(path.join(THIS_FOLDER, '.version')) as f:
    VERSION = f.read()

# Get long description from README.rst file
with open(path.join(THIS_FOLDER, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='codebox',
    version=VERSION,
    author='Wilson Santos',
    author_email='wilson@codeminus.org',
    url='https://gitlab.com/cathaldallan/codebox',
    description='Python utility code collection',
    long_description=LONG_DESCRIPTION,
    license='MIT',
    keywords='dict, yaml, dir',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'PyYAML',
        'jinja2'
    ],
)
