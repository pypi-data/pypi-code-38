#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['cloudevents==0.2.3']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="The Elegant Monkeys",
    author_email='contact@elegantmonkeys.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A HTTP server for listening to Knative Eventing messages",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='knative kubernetes cloudevents',
    name='kncloudevents',
    packages=find_packages(include=['kncloudevents']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/elegantmonkeys/python-kncloudevents',
    version='0.1.0',
    zip_safe=False,
)
