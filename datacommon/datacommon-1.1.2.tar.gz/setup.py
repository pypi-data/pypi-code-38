# -*- coding： utf-8 -*-
# author：pengr
from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name="datacommon",
    version="1.1.2",
    author="pengr",
    author_email="pengrui55555@163.com",
    description="A simple framework about data analysis.",
    long_description=open("readme.md", encoding="utf-8").read(),
    license="MIT",
    url="https://github.com/duiliuliu/OpenDataMS-spider",
    packages=['datacommon'],
    install_requires=[
        "xlwt",
        "xlsxwriter",
        "xlrd",
        "chardet"
    ],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Natural Language :: Chinese (Simplified)',
        'Topic :: Communications :: Email',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Internet',
        'Topic :: Software Development :: Version Control :: Git',
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
    ],
)
