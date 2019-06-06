# _*_ coding=utf-8 _*_
__author__  = "8034.com"
__date__    = "2018-05-03"

from setuptools import setup, find_packages
import sys
import os

# 如果是Windows，显示“nt”，如果是Linux，则“posix”
if os.name == u"nt":
    os.system("cd xxmind/file/xmind-sdk-python-master & python setup.py install & cd ../../..")
    # xmind_tar_gz = "http://qa.ymmoa.com/wrench/file/xmind-0.1a0.tar.gz"
else:
    os.system("cd xxmind/file/xmind-sdk-python-master && python setup.py install && cd ../../..")
    pass

from xxmind.__version__ import __VERSION__

setup(
    name="xxmind",
    version = __VERSION__,
    author="goblinintree",
    author_email="goblinintree@126.com",
    description="xxmind是将xmind固定格式转为xlsx的转换工具。",
    long_description=open("README.md",encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
    platforms=["all"],
    license="MIT",
    keywords = ['xlsx', 'excel', 'xmind'],
    url="https://pypi.org/project/xxmind/#description",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=True,
    install_requires=[
        "xlrd",
        "xlutils",
        "xlwt",
        "openpyxl",
    ],
    dependency_links = [
    ],
)