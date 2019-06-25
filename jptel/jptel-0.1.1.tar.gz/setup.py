# -*- coding=utf-8 -*-
from setuptools import setup, find_packages
import os


long_description = 'Japanese Telephone Number Utility'
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()

setup(
    name='jptel',
    version='0.1.1',
    description='Japanese Telephone Number Utility',
    long_description=long_description,
    license='MIT',
    author='zenwerk',
    author_email='zenwerk@gmail.com',
    url='https://github.com/zenwerk/jptel-py',
    keywords='japaneses telephone number',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ]
)
