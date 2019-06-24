#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    "biopython",
    "numpy",
    "pandas",
]

test_requirements = [
    "pytest",
]

setup(
    name='refchooser',
    version='0.1.0',
    description="Tools to help choosing a reference assembly.",
    long_description=readme + '\n\n' + history,
    author="Steve Davis",
    author_email='steven.davis@fda.hhs.gov',
    url='https://github.com/CFSAN-Biostatistics/refchooser',
    packages=[
        'refchooser',
    ],
    package_dir={'refchooser':
                 'refchooser'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords=['bioinformatics', 'NGS', 'refchooser'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={'console_scripts': ['refchooser = refchooser.cli:main']},
    setup_requires=["pytest-runner"],
    tests_require=test_requirements
)
