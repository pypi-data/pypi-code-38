#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: LiangjunFeng
# Mail: zhumavip@163.com
# Created Time:  2018-4-16 19:17:34
#############################################

from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="youda",  # 这里是pip项目发布的名称
    version="1.0.0",  # 版本号，数值大的会优先被pip
    keywords=("youda",),
    description="youdacloud",
    long_description="使用youda云",
    license="MIT Licence",

    url="http://www.youda.com.cn",  # 项目相关文件地址，一般是github
    author="zsd",
    author_email="2758474300@qq.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    # install_requires=["numpy"]  # 这个项目需要的第三方库
)
