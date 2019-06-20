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
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    description = 'Django Congo contains many useful tools for faster and more efficient Django application developing.',
    long_description = README,
    long_description_content_type = 'text/markdown',
    url = 'https://integree.eu/en/solutions/congo/',
    download_url = 'https://pypi.python.org/packages/source/d/django-congo/django-congo-%s.zip' % VERSION,
    author = 'Integree Bussines Solutions',
    author_email = 'hello@integree.eu',
    keywords = 'django-congo congo django utils integree',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django :: 1.11',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = [
        'django-admin-tools~=0.8.0',
        'django-appconf~=1.0.0',
        'django-bower~=5.2.0',
        'django-filter~=2.1.0',
        'django-mptt~=0.9.0',
        'django-parler~=1.9.0',

        'pillow~=4.1.0',
        'premailer~=3.1.0',
        'py_moneyed~=0.8.0',
        'pycryptodome~=3.6.0',
        'suds-jurko~=0.6.0',
        'unidecode~=1.0.0',
    ],
    zip_safe = False)
