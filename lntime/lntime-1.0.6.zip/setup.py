from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="lntime",
    version="1.0.6",
    author="lannan",
    author_email="865377886@qq.com",
    description="extract Time",
    long_description=open("README.rst",encoding="utf8").read(),
 
    url="https://github.com/lanmengfei/testdm",
    packages=['lntime'],

    install_requires=[

        "beautifulsoup4>=4.6.3",


        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ],
)