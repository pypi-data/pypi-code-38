#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-08-24 15:07:27
'''
import sys
if sys.version_info < (3, 6):
    sys.exit('Python 3.6 or greater is required.')

import os
import kk
from setuptools import setup, find_packages

data_files = []
os.chdir('kk')
for dirname in ['templates', 'static']:
    for root, _, files in os.walk(dirname):
        data_files.extend([os.path.join(root, fname) for fname in files])
os.chdir('..')

setup(
    name="kk",
    version=kk.__version__,
    description="a simple upload server",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="zhangkai",
    author_email="zkdfbb@qq.com",
    url="http://www.ishield.cn",
    license="MIT",
    python_requires='>=3.6',
    install_requires=["markdown", "pyaml", "pymongo", "tornado>=5.1"],
    package_data={'': data_files},
    packages=find_packages(),
    entry_points={
        'console_scripts': ['kk=kk.index:main']
    },
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # 属于什么类型
        'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
