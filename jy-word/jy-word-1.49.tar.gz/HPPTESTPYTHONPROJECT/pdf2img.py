# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/6/28 0028
__author__ = 'huohuo'
import os
import PythonMagick
from PythonMagick import Image
bgcolor = '#FFFFFF'


def pdf2img(input_pdf, postfix='.png', **kwargs):
    img = Image(input_pdf)
    img.density('300')
    size = "%sx%s" % (img.columns(), img.rows())
    output_img = Image(size, bgcolor)
    output_img.type = img.type
    output_img.composite(img, 0, 0, PythonMagick.CompositeOperator.SrcOverCompositeOp)
    output_img.resize(str(img.rows()))
    output_img.magick('JPG')
    output_img.quality(75)
    if 'out_path' in kwargs:
        output_jpg = kwargs['out_path']
    else:
        output_jpg = input_pdf.replace(".pdf", postfix)
    if os.path.exists(output_jpg):
        os.remove(output_jpg)
    output_img.write(output_jpg)

if __name__ == "__main__":
    pdf2img('D:\pythonproject\\report\data\part1\\tmb.pdf')
    pass
    

