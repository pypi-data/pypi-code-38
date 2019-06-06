#!/usr/bin/env python

import json

from setuptools import setup, find_packages

_PACKAGE_FILE = './package.json'
_README_FILE = './README.md'
_REQUIREMENTS_FILE = './requirements.txt'

with open(_PACKAGE_FILE, 'r') as file:
    package = json.load(file)

with open(_README_FILE, "r") as file:
    long_description = file.read()

with open(_REQUIREMENTS_FILE, 'r') as file:
    requirements = file.read().splitlines()

print(long_description)

setup(
    name=package['name'],
    version=package['version'],
    description=package['description'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=package['url'],
    license=package['license'],
    author='Taylor Steinberg',
    author_email='taylor.steinberg@lifeomic.com',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ],
)
