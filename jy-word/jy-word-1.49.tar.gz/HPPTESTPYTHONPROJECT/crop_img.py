# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/7/16 0016
__author__ = 'huohuo'
from PIL import Image

img = Image.open(r'D:\pythonproject\report\data\4.5.1signature.png')
sp = img.size
w, h = sp[0], sp[1]
region = (0, h/3, w, h/3 * 2)

#裁切图片
cropImg = img.crop(region)

#保存裁切后的图片
cropImg.save(r'D:\pythonproject\report\data\4.5.1signature1.png')

if __name__ == "__main__":
    pass
    

