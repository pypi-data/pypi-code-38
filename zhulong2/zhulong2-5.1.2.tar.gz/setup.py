from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="zhulong2",

    version="5.1.2",

    author="lanmengfei",
    author_email="865377886@qq.com",
    description="深圳市筑龙科技的工作-政府采购",
    long_description=open("README.txt",encoding="utf8").read(),
    

    url="https://github.com/lanmengfei/testdm",

    packages=find_packages(),

    package_data={#"zhulong.hunan":["profile"]
    "zhulong2.util":["cfg_db"],
    "zhulong2.guangdong":["yzm_model.m"]
  
    },

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
        "lmf>=2.0.6",
        "lmfscrap>=1.1.0",
        "lmfhawq>=1.2.0",
        "opencv-python",
        "scikit-learn",
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



