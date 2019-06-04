#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import io

import setuptools
import os
import requests


# 将markdown格式转换为rst格式
def md_to_rst(from_file, to_file):
    r = requests.post(url='http://c.docverter.com/convert',
                      data={'to': 'rst', 'from': 'markdown'},
                      files={'input_files[]': open(from_file, 'rb')})
    if r.ok:
        with open(to_file, "wb") as f:
            f.write(r.content)


md_to_rst("README.md", "README.rst")

if os.path.exists('README.rst'):
    long_description = open('README.rst', encoding="utf-8").read()
else:
    long_description = 'Add a fallback short description here'

if os.path.exists("requirements.txt"):
    install_requires = io.open("requirements.txt").read().split("\n")
else:
    install_requires = []

setuptools.setup(
    name="zhujunhua-common",
    version="0.0.3",
    author="ZhuJunhua",
    license='MIT License',
    author_email="a61231005@gmail.com",
    description="Common model for other project",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://test.pypi.org/user/pythonslave/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=install_requires,  # 常用
    # include_package_data=True,  # 自动打包文件夹内所有数据
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        'ifly-common': ['source/*.txt', "source/*.json"],
    }
)
