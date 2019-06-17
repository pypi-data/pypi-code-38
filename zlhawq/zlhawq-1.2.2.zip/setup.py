from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="zlhawq",
    version="1.2.2",
    author="lanmengfei",
    author_email="865377886@qq.com",
    description="兰孟飞深圳市筑龙科技的工作",
    long_description=open("README.rst",encoding="utf8").read(),
 
    url="https://github.com/lanmengfei/testdm",
     packages=find_packages(),
     package_data={"zlhawq.dag":['template/*']},
    install_requires=[
        "pandas >= 0.13",

        "lmf>=2.1.2",
        "psycopg2-binary",
        "requests",
        "lxml",
        "pycryptodome",
        "wget"

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