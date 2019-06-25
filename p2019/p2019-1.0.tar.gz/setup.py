#coding=utf-8
from distutils.core import setup
setup(
    name='p2019',#对外我们模块的名字
    version='1.0',#版本号
    description='这是第一个对外发布的模块，测试哦',#描述
    author='wyj',#作者
    author_email='925415925@qq.com',#邮箱
    py_modules=['p2019.snow','p2019.jiaodu']#要发布的模块
)