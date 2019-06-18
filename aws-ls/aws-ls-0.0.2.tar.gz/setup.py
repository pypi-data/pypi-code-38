# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    # pip install nnn
    name="aws-ls",
    version="0.0.2",
    keywords=("aws"),
    description="aws ls tools",
    long_description="aws ls tools",
    # 协议
    license="GPL Licence",

    url="https://github.com/xxx",
    author="elon",
    author_email="iphone1945@126.com",

    # 自动查询所有"__init__.py"
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    # 提示前置包
    install_requires=['PrettyTable'],

    # 注意 mypackage是命令名称，=后面的是包名以及函数名
    entry_points={
        'console_scripts': [
            'awsls = aws_ls.lib:foo',
        ]
    }
)

