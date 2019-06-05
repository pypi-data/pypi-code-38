#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: WangJY

from os.path import dirname, join
# from pip.req import parse_requirements

# 包管理工具
from setuptools import (
    find_packages,
    setup
)

with open(join(dirname(__file__), './VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()
    '''
        作为一个合格的模块，应该有版本号
    '''

mdpath = "./README.rst"

setup(
    name='ctec-utils',  # 模块名
    version=version,  # 版本号
    description='working tool',  # 标题描述
    packages=find_packages(exclude=[]),  # 包含目录中所有包，exclude=['哪些文件除外']
    author='wangjy',  # 作者
    author_email='1149447019@qq.com',  # 作者邮箱
    license='Apache License v2',
    package_data={'': ['*.*']},  # {'包名': ['正则']}
    url='https://github.com/poqweur/ctec-utils.git',
    # install_requires=[str(ir.req) for ir in parse_requirements("requirements.txt", session=False)],  # 所需的运行环境
    install_requires=[
        "msgpack==0.5.6",
        "pika==0.13.1",
        "requests==2.20.0",
        "DBUtils==1.3",
        "cx_Oracle==7.1.1",
        "redis-py-cluster==1.3.4",
        "redis==2.10.6",
        "pymongo==3.8.0",
        "pymysql==0.9.3",
        "six==1.12.0",
        "kafka-python==1.4.6",
        "logstash-formatter==0.5.17"
    ],
    long_description=open(mdpath, "r", encoding="utf-8").read() + "\r\n",
    long_description_content_type='text/markdown',
    data_files=[mdpath],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)