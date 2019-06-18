#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-SQLAlchemy-Caching',
    version='1.0.4',
    description='CachingQuery implementation to Flask using Flask-SQLAlchemy and Flask-Caching',
    author='Brad Belyeu',
    author_email='bradleylamar@gmail.com',
    url='http://www.github.com/bbelyeu/Flask-SQLAlchemy-Caching',
    download_url='https://github.com/bbelyeu/Flask-SQLAlchemy-Caching/archive/1.0.4.zip',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    platforms='any',
    packages=['flask_sqlalchemy_caching'],
    install_requires=[
        'Flask>=0.12.2',
        'Flask-Caching>=1.3.2',
        'Flask-SQLAlchemy>=2.2',
    ],
    test_suite='flask_sqlalchemy_caching.tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['flask', 'sqlalchemy', 'caching', 'cache'],
)
