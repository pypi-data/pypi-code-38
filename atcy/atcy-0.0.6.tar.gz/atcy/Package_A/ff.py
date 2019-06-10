# # 1.目录结构
# #
# # d:\atcy\atcy\__init__.py           注1
# # d:\atcy\atcy\Package_A\__init__.py 注2
# #             \Package_A\Model_A1.py
# #             \Package_A\Model_A2.py
# #             \Package_A\Model_A3.py
# # d:\atcy\atcy\Package_B\__init__.py 注3
# #             \Package_B\Model_B1.py
# #
# # d:\atcy\LICENSE
# #        \MANIFEST.in
# #        \README.rst
# #        \requirements.txt
# #        \setup.py
# #        \text.log
# #
# # 2.文件内容
# # =============================================
# # 2.1.__init__.py           注1
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# #
# # """atcy包的文档......"""
# #
# # from . import Package_A
# # import atcy.Package_B as Package_B
# # ==============================================
# # 2.2.__init__.py           注2
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# # """atcy.Pcakge_A包的文档......"""
# # from . import Model_A1
# # from . import Model_A2
# # from . import Model_A3
# # ===============================================
# # 2.3.__init__.py           注3
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# #
# # """atcy.Pcakge_B包的文档....."""
# # from .import Model_B1
# # ================================================
# # 2.4.Model_A1.py文档
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# # """atcy.Pcakge_A.Model_A1文档......"""
# # import sys
# # sys.path.append('../')
# # __doc__="""
# # author:tcy
# # Model A1 doc"""
# # __all__ = ["add", "view"]
# # __author__='tcy'
# # a1=100
# # def add(x,y):
# #     """
# #     add doc...
# #     """
# #     return x+y
# # def view():
# #     print('a1=',a1)
# # ==================================================
# # 2.5.Model_A2.py文档
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# # """atcy.Pcakge_A.Model_A2文档......"""
# #
# # import sys
# # sys.path.append('../')
# #
# # a2=200
# # def sub(x,y):
# #     """
# #     sub doc...
# #     """
# #     return x-y
# # ==================================================
# # 2.6.Model_A3.py文档
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# # """atcy.Pcakge_A.Model_A3文档......"""
# # import sys
# # sys.path.append('../')
# #
# #
# # import math
# # a3=300
# # def mul(x,y):
# #     """
# #     mul doc...
# #     """
# #     return x*y
# # def sin(x):
# #     return math.sin(x)
# # ==================================================
# # 2.7.Model_B1.py文档
# # # !/usr/bin/python3
# # # -*- coding: utf-8 -*-
# # """atcy.Pcakge_B.Model_B1文档......"""
# # import sys
# # sys.path.append('../')
# #
# # b1=400
# # def div(x,y):
# #     """
# #     div doc...
# #     """
# #     return x/y
# #
# # class B:
# #     """
# #     class doc...
# #     """
# #     def __init__(self,x,y):
# #         self.x=x;self.y=y
# #     def get_x(self):
# #         """
# #         get_x doc...
# #         """
# #         return self.x
# #     def set_x(self,x):
# #         """
# #         set_x doc...
# #         """
# #         self.x=x
# #
# #     def show(self):
# #         """
# #         show doc...
# #         """
# #         print('x=',self.x,'y=',self.y)
# #
# # ==================================================
# # 2.8.MANIFEST.in
# # recursive-include README.rst
# # recursive-include requirements.txt
# # recursive-include LICENSE
# # recursive-include text.log
# # recursive-include atcy *
# # ==================================================
# # 2.9.setup.py文档
# # #!/usr/bin/env python
# # # -*- coding: utf-8 -*-
# #
# # import setuptools
# # import send2trash
# # send2trash.send2trash(r'D:\atcy\.idea')
# # send2trash.send2trash(r'D:\atcy\build')
# # send2trash.send2trash(r'D:\atcy\dist')
# # send2trash.send2trash(r'D:\atcy\atcy.egg-info')
# #
# #
# # with open("README.rst", "r",encoding='utf-8') as fh:
# #     long_description = fh.read()
# #
# # setuptools.setup(
# #
# #     name="atcy",
# #     version="0.0.4",
# #
# #     author="Tcy",
# #     author_email="979442421@qq.com",
# #     description="A small example package测试包",
# #     long_description=long_description,
# #     # long_description_content_type=long_description,#"text/markdown",
# #     url="https://github.com/pypa/sampleproject",
# #     packages=setuptools.find_packages(),
# #     # packages=find_namespace_packages(include=['atcy.*']),
# #     keywords=("atcy",'Package_A1'),
# #     include_package_data=True,
# #     # classifiers=[
# #     #     "Programming Language :: Python :: 3",
# #     #     "License :: OSI Approved :: MIT License",
# #     #     "Operating System :: Windows",
# #     # ],
# # )
# # ==================================================
# # 2.10.README.rst文档
# # 软件相关说明
# # ==================================================
# # 2.11.requirements.txt
# # matplotlib>=1.5.2
# # numpy>=1.11.1
# # scipy>=0.18.0
# # ==================================================
# # 2.12.text.log
# # 安装相关说明
# # ==================================================
# # 2.13.LICENSE
# # # The MIT License (MIT)
# #
# # CopyRight (c) 2015 omi &lt;<a href="4399.omi@gmail.com">4399.omi@gmail.com</a>&gt;
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in
# # all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# # THE SOFTWARE.
# # ==================================================
# Restarting kernel...
#
#
#
#
# import atcy
#
# atcy?
# Type:        module
# String form: <module 'atcy' from 'C:\\ProgramData\\Anaconda3\\lib\\site-packages\\atcy\\__init__.py'>
# File:        c:\programdata\anaconda3\lib\site-packages\atcy\__init__.py
# Docstring:   包的文档atcy+111111111111111111111111111111111111111111
#
# from atcy.Package_A import Model_A2
#
# atcy.Package_A?
# Type:        module
# String form: <module 'atcy.Package_A' from 'C:\\ProgramData\\Anaconda3\\lib\\site-packages\\atcy\\Package_A\\__init__.py'>
# File:        c:\programdata\anaconda3\lib\site-packages\atcy\package_a\__init__.py
# Docstring:   ----------aaaaaaaa-------------------------
#
# Model_A2?
# Type:        module
# String form: <module 'atcy.Package_A.Model_A2' from 'C:\\ProgramData\\Anaconda3\\lib\\site-packages\\atcy\\Package_A\\Model_A2.py'>
# File:        c:\programdata\anaconda3\lib\site-packages\atcy\package_a\model_a2.py
# Docstring:   Model A2 doc
#
# Model_A2.a2
# Out[6]: 200
#
# Model_A2.sub?
# Signature: Model_A2.sub(x, y)
# Docstring: Sub function doc...
# File:      c:\programdata\anaconda3\lib\site-packages\atcy\package_a\model_a2.py
# Type:      function
#
# Model_A2.sub(2,3)
# Out[8]: -1
#
# atcy.Package_A.Model_A1?
# Type:        module
# String form: <module 'atcy.Package_A.Model_A1' from 'C:\\ProgramData\\Anaconda3\\lib\\site-packages\\atcy\\Package_A\\Model_A1.py'>
# File:        c:\programdata\anaconda3\lib\site-packages\atcy\package_a\model_a1.py
# Docstring:
# author:tcy
# Model A1 doc...
#
# from atcy.Package_B import Model_B1
#
# from atcy.Package_B import Model_B1 as e
#
# a=e.B(222,333)
#
# a.get_x()
# Out[13]: 222
#
# a.set_x(1000)
#
# a.x
# Out[15]: 1000
#
# a.show()
# x= 1000 y= 333
