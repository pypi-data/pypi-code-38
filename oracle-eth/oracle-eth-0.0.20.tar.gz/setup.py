#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, sys, shutil

py_version = sys.version_info[:2]

if py_version <= (2, 7):
    raise RuntimeError('On Python 2, Oracle not Support !')
elif (3, 0) < py_version < (3, 6):
    raise RuntimeError('On Python 3, Oracle requires Python 3.6 or later')


# copy oracle.conf -> /etc/oracle.conf
here = os.path.abspath(os.path.dirname(__file__))
# 用于组织的配置文件
shutil.copyfile(os.path.join(here, 'oracle.cfg'), '/etc/oracle.cfg')
# 用于军队事务的配置文件
shutil.copyfile(os.path.join(here, 'oracle_army.cfg'), '/etc/oracle_army.cfg')

try:
    README = open(os.path.join(here, 'README.md')).read()
    print(README)
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = """
oracle 是一个智能协约的管理程序，用于导入event的数据到数据库中，和处理event数据
"""
    CHANGES = ''


setup(
    name="oracle-eth",
    version="0.0.20",
    author="yuyongpeng",
    author_email="yuyongpeng@hotmail.com",
    description=("这是一个event监听程序，用于数据交换"),
    # long_description=README + '\n\n' + CHANGES,
    # long_description_markdown_filename='README.md',
    # long_description_content_type="text/markdown",
    # license="MIT",
    license=open('LICENSE').read(),
    keywords="solidity web3 constract sdk",
    url="https://gitlab.hard-chain.cn/cport/oracle",
    # packages=['oracle'],  # 需要打包的目录列表
    packages=find_packages(where='.', exclude=('tests', 'tests.*'), include=('*',)),
    # 需要安装的依赖
    install_requires=[
        'pycontractsdk',    # 对web3的封装
        'sierra-utils-rand',
        'clock',
        'peewee==3.9.3',
        'arrow==0.13.1',
        'pymysql==0.9.3',
        'celery==4.3.0',
        'pika==1.0.0',
        'kafka==1.3.5',
        'retry==0.9.2',
        'redis==3.2.1',
        'requests==2.21.0',
        #logzero
        'logbook==1.4.3',
        'toolz==0.9.0',
        'wrapt==1.11.1',
        'click==7.0',
        'random2',
        'python-common-cache==0.1',
        'wechatpy[cryptography]==1.8.1',
        'cryptography==2.6.1',
        'rsa==4.0',
        'hexbytes==0.1.0',
    ],
    py_modules=['oracle'],
    python_requires='>=3.6',
    setup_requires=['setuptools-markdown'],
    # 添加这个选项，在windows下Python目录的scripts下生成exe文件
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        'army = oracle.main:army',                            # 军队端 oracle
        'organization = oracle.main:organization',            # organization 的 oracle  (事务部)
        'impevent = oracle.main:impevent',                    # 把 DIDRegistry.sol 中的 event 数据导入到数据库中
    ]},
    # 会把这个list中的文件copy到系统的PATH路径下
    scripts=['run.sh'],
    # long_description=read('README.md'),
    classifiers=[  # 程序的所属分类列表
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Topic :: Utilities",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe=False
)