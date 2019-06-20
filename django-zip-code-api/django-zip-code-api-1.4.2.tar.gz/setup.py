# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

from zip_code_api import VERSION

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-zip-code-api',
    version = VERSION,
    author = 'Integree Bussines Solutions',
    description = 'Zip Code API is an API for zip codes (postal codes) and addresses requesting. Optimized for polish addresses, however might work as universal tool.',
    long_description = README,
    long_description_content_type = "text/markdown",
    url = 'https://integree.eu/en/solutions/zip-code-api/',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 1.11",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires = [
        'django',
        'django-appconf',
        'requests',
    ],
)
