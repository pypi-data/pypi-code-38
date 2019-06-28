from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="parse_diqu",

    version="1.0.11",

    author="lanmengfei",
    author_email="865377886@qq.com",
    description="深圳市筑龙科技的工作-解析地区编号",
    long_description=open("README.txt", encoding="utf8").read(),

    url="https://github.com/lanmengfei/testdm",

    packages=find_packages(),

    package_data={  # "zhulong.hunan":["profile"]
        "parse_diqu": ["xzqh_key_word.json"],
    },

    install_requires=[
        "jieba",
        "beautifulsoup4>=4.6.3",
        "lmf>=2.0.6",
        "lmfscrap>=1.1.0",
        "lmfhawq>=1.1.4"
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
