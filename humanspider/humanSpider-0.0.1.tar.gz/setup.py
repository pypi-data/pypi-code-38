import os
import sys

from setuptools import setup, find_packages

setup(
    name='humanSpider',
    version='0.0.1',
    packages=find_packages(),
    description='simple python spider util',
    long_description='',
    author='JYangHe',
    author_email='jyanghe1023@gmail.com',
    url='https://github.com/JYangHE/humanSpider',
    license='BSD License',
    platforms=["all"],
    classifiers=(
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ),
    install_requires=[
        'beautifulsoup4',
        'bloom-filter',
        'bs4',
        'lxml',
        'requests'
    ],
    zip_safe=False,
)
