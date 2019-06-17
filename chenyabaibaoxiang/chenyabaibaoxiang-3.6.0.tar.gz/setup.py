#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: mage
# Mail: mage@woodcol.com
# Created Time: 2018-1-23 19:17:34
#############################################


from setuptools import setup, find_packages

setup(
    name="chenyabaibaoxiang",
    version="3.6.0",
    keywords=("dashu", "baibaoxiang"),
    description="this is novice help",
    long_description="Welcome to the testing family. This is my little help to you",
    license="test Licence",

    url="https://www.baidu.com",
    author="dashu",
    author_email="bj_xiaoya@163.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
	install_requires=[]
    #install_requires=["selenium","wheel","xlwt","pymysql","smtplib","pillow","pytesseract","requests","traceback"]
)

'''
先进入项目setup.py所在路径
打包版本
python setup.py sdist
上传
twine upload dist/chenyabaibaoxiang-3.6.0.tar.gz
安装
pip install chenyabaibaoxiang==1.0.0
'''