from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="gzqzl",
    version="1.2.9",
    author="gzq",
    author_email="1261873524@qq.com",
    description="zl四库一平台",
    long_description=open("README.txt", encoding="utf8").read(),
    url="https://github.com/",
    packages=find_packages(),
    package_data={"gzqzl":["cfg_db","cfg2_db","cfg3_db"],},

    install_requires=[
        "pandas >= 0.13",
        "beautifulsoup4>=4.6.3",
        "cx-Oracle",
        "numpy",
        "psycopg2-binary",
        "selenium",
        "xlsxwriter",
        "xlrd",
        "requests",
        "lxml",
        "sqlalchemy",
        "pymssql",
        "jieba",
        "mysqlclient",
        "pymssql",
        "lmf",
        "lmfscrap",
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


