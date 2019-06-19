#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

from django_media_placeholder.meta import VERSION

setup(
    name='django_media_placeholder',
    version=str(VERSION),
    description='Process every media request, if media not present locally, and try to obtain in another location',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Shinneider Libanio da Silva',
    author_email='shinneider-libanio@hotmail.com',
    url='https://github.com/shinneider/django_media_placeholder',
    license='MIT',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    python_requires=">=3.3",
)
