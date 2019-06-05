#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'unicodecsv >= 0.14.1',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='docdown',
    version='0.2.2',
    description="DocDown is a Markdown extension for source code documentation.",
    long_description=readme + '\n\n' + history,
    author="Jason Emerick, Justin Michalicek",
    author_email='jason@mobelux.com, justin@mobelux.com',
    url='https://github.com/livio/DocDown-Python',
    packages=[
        'docdown',
        'docdown.template_adapters'
    ],
    package_dir={'docdown': 'docdown'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords=['docdown', 'markdown', 'documentation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
