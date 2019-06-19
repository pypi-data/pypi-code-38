from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="zlairflow",

    version="1.1.7",

    author="lanmengfei",
    author_email="865377886@qq.com",
    description="深圳市筑龙科技的工作",
    long_description=open("README.txt",encoding="utf8").read(),
    package_data={
    "zlairflow.dag":['template/*']
    },

    url="https://github.com/lanmengfei/testdm",

    packages=find_packages(),

    install_requires=[
        "lmf>=2.0.6",
        "fabric"
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



