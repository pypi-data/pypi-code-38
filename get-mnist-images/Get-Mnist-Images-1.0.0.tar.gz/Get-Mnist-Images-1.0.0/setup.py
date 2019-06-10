#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "Get-Mnist-Images",      #这里是pip项目发布的名称
    version = "1.0.0",  #版本号，数值大的会优先被pip
    keywords = ("pip", "Mnist","Images"),
    description = "将Mnist中的数据保存成本地PNG格式的图片",
    long_description = "将Mnist中的数据保存成本地PNG格式的图片",
    license = "MIT Licence",

    url = "",     #项目相关文件地址，一般是github
    author = "Luskyle",
    author_email = "844804539@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy","pillow"]          #这个项目需要的第三方库
)
