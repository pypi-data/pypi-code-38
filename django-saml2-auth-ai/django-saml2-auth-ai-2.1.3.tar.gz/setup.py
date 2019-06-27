"""
The setup module for django_saml2_auth_ai.
"""

from codecs import open
from setuptools import (setup, find_packages)
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name='django-saml2-auth-ai',
    version='2.1.3',

    description='Django SAML2 Authentication AI',
    long_description=long_description,

    url='https://github.com/andersinno/django-saml2-auth-ai',

    author='Anders Innovations',
    author_email='info@anders.fi',

    license='Apache 2.0',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Django, SAML2, authentication, SSO',

    packages=find_packages(),

    install_requires=['pysaml2>=4.5.0'],
    include_package_data=True,
)
