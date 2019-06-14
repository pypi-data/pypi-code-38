import glob
import os
import re

from setuptools import find_packages
from setuptools import setup

PACKAGE_NAME = 'sloth_cli'
MY_DIRECTORY = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.join(MY_DIRECTORY, PACKAGE_NAME)


def get_version():
    """Returns the version"""
    path = os.path.join(MY_DIRECTORY, 'sloth_cli', '__init__.py')
    with open(path, 'r') as f:
        return (
            re.compile(r'\n__version__\s+=\s+\'(?P<version>[0-9.]+)\'')
            .search(f.read())
            .group('version')
        )


def readme():
    """Returns the read me text"""
    path = os.path.realpath(os.path.join(
        os.path.dirname(__file__),
        'README.md'
    ))
    with open(path) as f:
        return f.read()


def populate_extra_files():
    """
    Create a list of non-python data files to include in package distribution
    """

    globs = [
        '{}/**/*.json'.format(PACKAGE_ROOT),
        '{}/**/*.txt'.format(PACKAGE_ROOT),
        '{}/**/*.jinja2'.format(PACKAGE_ROOT),
        '{}/**/*.sql'.format(PACKAGE_ROOT)
    ]

    return [
        item
        for glob_path in globs
        for item in glob.iglob(glob_path, recursive=True)
    ]


setup(
    name='sloth-cli',
    version=get_version(),
    description=(
        'A library to analyse how slow your code is. This is a quick way to '
        'validate what is slow in your code. '
    ),
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords=['cProfile', 'speed', 'cli', 'performance', 'slow'],
    url='https://github.com/rigogsilva/sloth-cli',
    author='Rodrigo da Silva',
    author_email='dasil021@umn.edu',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={'': populate_extra_files()},
    include_package_data=True,
    zip_safe=False,

    entry_points=dict(
        console_scripts=[
            'sloth=sloth_cli:run'
        ]
    ),

    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'coverage']
)
