#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='mam',
    version='0.0.1',
    license='MIT',
    description='Runs linters and outputs them all together.',
    long_description=None,
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://github.com/Peilonrayz/mam',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'nox',
        'PyYAML',
        'typing_extensions',
        'parse',
        'mypy_extensions',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='linter',
    entry_points={
        "console_scripts": [
            "mam=mam.__main__:main"
        ]
    },
)
