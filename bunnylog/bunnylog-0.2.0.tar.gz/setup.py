#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name = "bunnylog",
    version = "0.2.0",
    packages = find_packages(),
    install_requires = ['testsimple>=0.1'],
    url = "https://github.com/gkbrk/bunnylog-py",
    author = "Gokberk Yaltirakli",
    author_email = "opensource@gkbrk.com",
    description = "BunnyCDN log parser",
    keywords = "parser cdn log BunnyCDN",
    project_urls = {
        'Bug Tracker': 'https://github.com/gkbrk/bunnylog-py/issues',
        'Source Code': 'https://github.com/gkbrk/bunnylog-py'
    }
)
