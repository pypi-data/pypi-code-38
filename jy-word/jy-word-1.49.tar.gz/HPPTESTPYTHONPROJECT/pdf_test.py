# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/7/5 0005
__author__ = 'huohuo'
import PythonMagick
from PyPDF2 import PdfFileReader
from pdf2img import pdf2img

C_RESOURCE_FILE=u'H:\晶云公司\\1.需求文档\下载报告\多组学临床检测报告\数据\part0'
C_PDFNAME=u'王其君100301检测报告.pdf'
C_JPGNAME=u'img\王其君100301检测报告%s.jpg'

input_stream = file(C_RESOURCE_FILE+'\\'+C_PDFNAME, 'rb')
pdf_input = PdfFileReader(input_stream,strict=False)    #错误1
page_count = pdf_input.getNumPages()

img = PythonMagick.Image()    # empty object first
img.density('300')           # set the density for reading (DPI); must be as a string
print page_count
for i in range(page_count):
    try:
        img.read(C_RESOURCE_FILE+'\\'+C_PDFNAME + ('[%s]'%i))     #分页读取 PDF
        imgCustRes = PythonMagick.Image(img)  # make a copy
        imgCustRes.sample('x1600')
        imgCustRes.write(C_RESOURCE_FILE+'\\'+(C_JPGNAME%i))
    except Exception, e:
        print e
        pass

print 'done'
if __name__ == "__main__":
    pass
    

