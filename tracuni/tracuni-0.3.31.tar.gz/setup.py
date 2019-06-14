#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # 'Click>=6.0',
    'typing;python_version<"3.6"',
    'aiozipkin>=0.4.0',
    'aiotask_context',
    "python-statsd",
    "pytz",
    "aioamqp",
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Konstantin Gonciarou",
    author_email='konstantin.goncharov@inplat.ru',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Convenient library to plug in tracer to incoming and "
                "outgoing points and extract data from there",
    entry_points={
        'console_scripts': [
            'tracuni=tracuni.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='jaeger zipkin tracer',
    name='tracuni',
    packages=find_packages(),
    python_requires='>=3.5.3',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hastly/tracuni',
    version='0.3.31',
    zip_safe=False,
)
