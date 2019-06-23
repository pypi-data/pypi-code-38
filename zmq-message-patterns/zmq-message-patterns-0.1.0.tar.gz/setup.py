# -*- coding: utf-8 -*-

from os import path
from codecs import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zmq-message-patterns',
    version='0.1.0',
    description='Library to quickly build ZeroMQ based applications.',
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    url='https://github.com/dansan/python-zmq-message-patterns/',
    author='Daniel Tröder',
    author_email='daniel@admin-box.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='zmq zeromq pyzmq sockets development parallel-processing concurrency',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['six', 'pyzmq'],
    project_urls={
        'Bug Reports': 'https://github.com/dansan/python-zmq-message-patterns/issues/',
        'Source': 'https://github.com/dansan/python-zmq-message-patterns/',
    },
    test_suite='tests',
)
