#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
        
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# see https://packaging.python.org/tutorials/packaging-projects/
setup(
#     固定部分
    name="kdGUI",
    version="1.0.0",
    author="bkdwei",
    author_email="bkdwei@163.com",
    maintainer="韦坤东",
    maintainer_email="bkdwei@163.com",
    long_description=long_description,
#     long_description_content_type="text/markdown",
    url="https://github.com/bkdwei/kdGUI",
    license="MIT",
    platforms=["any"],
    
#     需要安装的依赖
    install_requires=["ttkthemes"],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,

#     可变部分
    description="",
    keywords=("tkinter", "gui"),
#   see  https://pypi.org/classifiers/
    classifiers=[
        " Development Status :: 2 - Pre-Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Developers",
        "Natural Language :: Chinese (Simplified)",
        "Topic :: Software Development :: User Interfaces",
        "Programming Language :: Python :: 3",
        " License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
    ]
)
