#!/usr/bin/env python
import os
from setuptools import setup

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
README = open(os.path.join(ROOT_DIR, 'README.md')).read()

setup(
    name='django-kakao-zipcode',
    version='0.1.0',
    description='Kakao zipcode service widget for Django',
    long_description=README,
    author='Lee HanYeong',
    author_email='dev@lhy.kr',
    license='MIT',
    packages=[
        'kakao_zipcode',
    ],
    url='https://github.com/LeeHanYeong/django-kakao-zipcode',
    zip_safe=True,
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python',
    ]
)
