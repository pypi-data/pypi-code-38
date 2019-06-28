# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "click",
]

setup(
    name="tail",
    version="0.1.7",
    description="文件tail工具。引入“偏移量文件”记录文件读取信息，支持文件内容断续读取。",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/appstore-zencore/tail",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['tail', 'tailf'],
    install_requires=requires,
    packages=find_packages("."),
    py_modules=["tail"],
    entry_points={
        'console_scripts': [
            'pytail = tail:main',
        ]
    },
)