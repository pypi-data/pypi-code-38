#!/usr/bin/env python
from setuptools import setup

kwargs = {}

with open('mockry/version.py') as f:
    ns = {}
    exec(f.read(), ns)
    version = ns['version']

install_requires = ['tornado >= 6.0.2', 'tort >= 0.5.7', 'pycares >= 3.0.0', 'jsonpointer >= 2.0.0']


with open('README.md') as f:
    kwargs['long_description'] = f.read()
    kwargs['long_description_content_type'] = 'text/markdown'


python_requires = '>= 3.7'
kwargs['python_requires'] = python_requires

setup(
    name='mockry',
    version=version,
    description='mockry - A rich mock server you have searched for',
    url='https://github.com/glibin/mockry',
    download_url='https://github.com/glibin/mockry/tarball/{}'.format(version),
    packages=['mockry', 'mockry.test'],
    license='LICENSE',
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    **kwargs
)
