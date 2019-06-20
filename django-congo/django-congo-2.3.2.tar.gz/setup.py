# -*- coding: utf-8 -*-
from congo import VERSION
import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-congo',
    version = VERSION,
    author = 'Integree Bussines Solutions',
    description = 'Django Congo contains many useful tools for faster and more efficient Django application developing.',
    long_description = README,
    long_description_content_type = "text/markdown",
    url = 'https://integree.eu/en/solutions/congo/',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires = [
        'django-admin-tools~=0.8.0',
        'django-appconf~=1.0.0',
        'django-bower~=5.2.0',
        'django-mptt~=0.9.0',
        'django-parler~=1.9.0',

        'pillow~=4.1.0',
        'premailer~=3.1.0',
        'py_moneyed~=0.8.0',
        'pycrypto==2.6.1',
        'suds-jurko~=0.6.0',
        'unidecode~=1.0.0',
    ],
    zip_safe = False)
