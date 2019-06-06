# -*- coding: utf-8 -*-
__author__  = "8034.com"
__date__    = "2018-11-08"

import sys
print(sys.getdefaultencoding())
import os

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

class Main(object):
    if sys.version[:1] > '2':
        from xxmind.ui3 import Application
    else:
        from xxmind.ui2 import Application
    app = Application()
    # 窗口标题:
    app.master.title(u'Xmind转为xls文件')
    favicon_path = os.path.join(FILE_PATH, 'favicon.ico')
    app.master.iconbitmap(favicon_path)
    # 主消息循环:
    app.master.mainloop()
    pass