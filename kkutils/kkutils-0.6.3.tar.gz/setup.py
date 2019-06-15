#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2019-04-07 00:07:43
'''
from setuptools import setup


setup(
    name="kkutils",
    version="0.6.3",
    description="digua python utils",
    author="zhangkai",
    author_email="zkdfbb@qq.com",
    url="http://www.ishield.cn",
    license="MIT",
    python_requires='>=3.6',
    data_files=[('', ['requirements.txt']), ('utils', ['utils/user_agent.json'])],
    install_requires=[line.strip() for line in open('requirements.txt') if not line.strip().startswith('#')],
    include_package_data=True,
    py_modules=[
        'spider',
    ],
    packages=[
        'tornado_utils',
        'utils',
    ],
    classifiers=[
        # 发展时期
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
