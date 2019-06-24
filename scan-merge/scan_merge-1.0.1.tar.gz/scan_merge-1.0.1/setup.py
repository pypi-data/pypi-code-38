#!/usr/bin/env python3
"""Setuptools configuration."""

from os.path import abspath, dirname, join, normpath

from setuptools import setup, find_packages

setup(
    name='scan_merge',
    version='1.0.1',
    description='Tool to merge scanned PDFs from single sided document feeders',
    long_description=open(
        normpath(join(dirname(abspath(__file__)), 'README.md'))).read(),
    long_description_content_type="text/markdown",
    author='Arvid Norlander',
    author_email='VorpalBlade@users.noreply.github.com',
    url='https://github.com/VorpalBlade/scan_merge',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Graphics :: Capture :: Scanners',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'argcomplete',
        'funcy',
        'pypdf2'
    ],
    entry_points={'console_scripts': [
        'scan_merge=scan_merge:main',
    ]},
)
