# -*- coding:utf-8 -*-
from django.forms import Form, FileField

__author__ = 'denishuang'

class FileUploadForm(Form):
    file = FileField(label=u"文件")