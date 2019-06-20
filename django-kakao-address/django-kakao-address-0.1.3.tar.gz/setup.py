#!/usr/bin/env python
import os
from setuptools import setup

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
README = open(os.path.join(ROOT_DIR, 'README.md')).read()
VERSION = open(os.path.join(ROOT_DIR, 'version.txt')).read()

setup(
    name='django-kakao-address',
    version=VERSION,
    description='Kakao address service widget for Django',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Lee HanYeong',
    author_email='dev@lhy.kr',
    license='MIT',
    packages=[
        'kakao_address',
    ],
    url='https://github.com/LeeHanYeong/django-kakao-address',
    zip_safe=True,
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python',
    ]
)
