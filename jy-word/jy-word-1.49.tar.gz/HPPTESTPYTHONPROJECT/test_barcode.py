# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/9/29 0029
__author__ = 'huohuo'
from barcode.writer import ImageWriter
from barcode.codex import Code39
imagewriter = ImageWriter()
#保存到图片中
#add_checksum : Boolean   Add the checksum to code or not (default: True)
ean = Code39("1234567890", writer=imagewriter, add_checksum=False)
# 不需要写后缀，ImageWriter初始化方法中默认self.format = 'PNG'
print '保存到image.png'
ean.save('image')

if __name__ == "__main__":
    pass
    

