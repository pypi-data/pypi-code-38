# create by fanfan on 2019/5/29 0029
#!/usr/bin/env python
# Learn more: https://github.com/kennethreitz/setup.py
from distutils.core import setup
from setuptools import  find_packages
setup(
    name='triedTree',
    version='0.1.3',
    description='基于字典树实现实体发现',
    author='qiufengfeng',
    author_email='544855237@qq.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/fanfanfeng/triedTree',
    license='LGPL',
    #long_description=open("README.md",encoding='utf-8').read()
)
