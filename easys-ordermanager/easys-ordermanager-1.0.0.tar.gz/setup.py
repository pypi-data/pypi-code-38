# -*- coding: UTF-8 -*-
import os
from setuptools import setup, find_packages

import easys_ordermanager


def long_description():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    except IOError:
        return ''


def changelog():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.md')).read()
    except IOError:
        return ''


def requirements():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).readlines()
    except IOError:
        return []


setup(
    name=easys_ordermanager.__title__,
    packages=find_packages(),
    version=easys_ordermanager.__version__,
    description=easys_ordermanager.__description__,
    author=easys_ordermanager.__author__,
    author_email=easys_ordermanager.__author_email__,
    long_description=long_description() + '\n\n' + changelog(),
    long_description_content_type='text/markdown',
    install_requires=requirements(),
    license=easys_ordermanager.__license__,
    url=easys_ordermanager.__url__,
    download_url='',
    keywords=[],
    include_package_data=True,
    classifiers=[],
)
