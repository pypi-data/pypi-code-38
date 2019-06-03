#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('mediabyte/README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = [ 'youtube-dl','requests','pydub']

test_requirements = [ ]

setup(
    author="David Mekonnen Rønn",
    author_email='gh@v1d.dk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows :: Windows 10',
    ],
    description="A simple and succinct syntax for handling online media.",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='online media metadata tagging mixing sharing',
    name='mediabyte',
    packages=['mediabyte'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/taext/mediabyte',
    version='0.8.6.9',
    license='MIT',
    zip_safe=False,
)
