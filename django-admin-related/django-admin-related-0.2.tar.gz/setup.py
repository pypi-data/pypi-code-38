# -*- coding: utf-8 -*-
#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

from django_admin_related.meta import VERSION

setup(
    name='django-admin-related',
    version=str(VERSION),
    description='The "Django Admin Related" prevents you from deleting your models if you have related items',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Shinneider Libanio da Silva',
    author_email='shinneider-libanio@hotmail.com',
    url='https://github.com/shinneider/django_admin_related',
    license='MIT',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    python_requires=">=3.3",
)