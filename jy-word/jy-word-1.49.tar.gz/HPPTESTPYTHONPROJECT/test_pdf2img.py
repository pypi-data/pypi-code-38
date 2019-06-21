# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/11/10 0010
__author__ = 'huohuo'
import os
pdf_path = 'report2.pdf'
print os.path.exists(pdf_path)
import PythonMagick


try:
    im =PythonMagick.Image(pdf_path)
    im.density('300') #设置dpi，不设置估计就96dpi
    im.read(pdf_path+ '[' + str(p) +']')
    im.write('file_out-'+ str(p)+ '.png')
except:
    print "PythonMagick 产生错误:"
