#!/usr/bin/env python
#coding=utf-8
from distutils.core import setup
setup(
	  name="alter", #模块的名称
	  version="1.6",#版本号，每次修改代码的时候，可以改一下
	  description="send message to (wechat dtalk email)",#描述
	  long_description="[Github-flavored Markdown](https://github.com/lyy910203/Alter/blob/master/README.md)",
      #long_description_content_type="text/markdown",
	  author="Tommy Lin",#作者
	  author_email="351937287@qq.com",#联系邮箱
	  url="https://www.iyunw.cn",#你的主页
	  py_modules=['alter']#这个是下面有哪些模块可以用
	  )