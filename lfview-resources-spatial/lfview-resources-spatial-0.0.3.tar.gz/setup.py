#!/usr/bin/env python
"""Spatial resources for LF View API Python client"""

import setuptools

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
    'Topic :: Scientific/Engineering',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setuptools.setup(
    name='lfview-resources-spatial',
    version='0.0.3',
    packages=setuptools.find_packages(exclude=('tests',)),
    install_requires=[
        'properties[full]>=0.5.6',
        'lfview-resources-files',
    ],
    author='Seequent',
    author_email='franklin.koch@seequent.com',
    description='Definitions and documentation for LF View spatial resources',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    license='MIT',
    url='https://lfview.com',
    download_url='https://github.com/seequent/lfview-resources-spatial',
    classifiers=CLASSIFIERS,
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    use_2to3=False,
)
