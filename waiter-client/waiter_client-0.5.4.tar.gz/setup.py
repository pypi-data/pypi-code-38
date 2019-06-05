#!/usr/bin/env python3

from setuptools import setup

requirements = [
    'arrow==0.13.1',
    'humanfriendly==4.18',
    'requests==2.20.0',
    'tabulate==0.8.3'
]

test_requirements = [
    'pytest',
    'retrying'
]

extras = {
    'test': test_requirements,
}


def get_version():
    from waiter import version
    return version.VERSION


setup(
    name='waiter_client',
    version=get_version(),
    description="Two Sigma's Waiter CLI",
    long_description="This package contains Two Sigma's Waiter command line interface, waiter. waiter allows you to "
                     "create/update/delete/view tokens and also view services across multiple Waiter clusters.",
    packages=['waiter', 'waiter.subcommands'],
    entry_points={'console_scripts': ['waiter = waiter.__main__:main']},
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras
)
