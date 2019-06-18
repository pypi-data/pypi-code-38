#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-ucamwebauth',
    description='A Django authentication backend for Ucam-WebAuth a.k.a. Raven',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.developers.cam.ac.uk/uis/devops/django/ucamwebauth',
    # When changing this version number, remember to update
    # django-ucamwebauth.spec and debian/changelog.
    version='1.5.0',
    license='MIT',
    author='DevOps Division, University Information Services, University of Cambridge',
    author_email='raven-support@cam.ac.uk',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django>=1.11', 'pyOpenSSL'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
