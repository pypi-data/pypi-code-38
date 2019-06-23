#!/usr/bin/env python
# encoding: utf-8
"""
@author: 熊利宏
@email:xionglihong@163.com
@phone：15172383635
@project: xToolkit
@file: setup.py
@time: 2019-05-19 下午9:18
"""

from setuptools import setup, find_packages

# 导入信息说明文档
with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setup(
    # pip项目发布的名称
    name="xToolkit",
    # 版本号
    version="0.0.22",
    # 模块的关键词，使用空格分割
    keywords=("xToolkit", "xtoolkit", "x", "tool", "toolkit"),
    # 项目的简单描述：
    description="此库从新封装了python下常用的数据类型，在内置模块的基础扩展了部分功能.",
    # 单文件模块写法
    py_modules=[],
    # 项目详细描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 许可证
    license="MIT Licence",
    # 项目相关文件地址，一般是github
    url="https://github.com/xionglihong/xToolkit",
    # 作者姓名
    author="xionglihong",
    # 作者邮箱
    author_email="xionglihong@163.com",
    # 维护人员的名字
    maintainer='xionglihong',
    # 维护人员的邮箱
    maintainer_email='xionglihong@163.com',
    # 注意,这个地方参数要用英文,如果用中文会出现上传识别，不断重试之后还是失败
    classifiers=[
        # 当前开发进度等级的选项
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 3 - Alpha',  # 当前开发进度等级（测试版，正式版等）
        'Intended Audience :: Developers',  # 模块适用人群
        'Topic :: Software Development :: Build Tools',  # 给模块加话题标签
        'License :: OSI Approved :: MIT License',  # 模块的license
        'Programming Language :: Python :: 3',  # 模块支持的Python版本
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # 这个参数是导入目录下的所有__init__.py包
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    # 依赖库
    install_requires=["arrow>=0.13.2"]
)
