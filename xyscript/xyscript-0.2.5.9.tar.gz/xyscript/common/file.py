#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xyscript.config import Config
import stat
from xyscript.xylog import *
from xyscript.common import interaction
import zipfile

class File:
    def compress_file_with_password(self,file,password=None):
        pass
    
    def uncompress_file(self):
        zf = zipfile.ZipFile("/Users/v-sunweiwei/Desktop/saic/ziptest.zip")
        zf.extractall(pwd="1234")

    def make_pw_file(self):
        num_array = "1234567890"
        capital_case_array = "ZXCVBNMASDFGHJKLQWERTYUIOP"
        lower_case_array = "zxcvbnmasdfghjklqwertyuiop"
        special_character_array = "~!@#$%^&*()_+;:\'\",./<>?\|\b"

        inter = Interaction()
        num = inter.get_user_input("是否存在数字(y/n)")
        capital_case = inter.get_user_input("是否存在大写字母(y/n)")
        lower_case = inter.get_user_input("是否存在小写字母(y/n)")
        special_character = inter.get_user_input("是否存在特殊字符(y/n)")
        max_length = inter.get_user_input("最大长度")
        min_length = inter.get_user_input("最小长度")

    def progressbar(self,nowprogress,total):
        get_progress = int((nowprogress + 1) * (50/total))
        get_pro = int(50 - get_progress)
        percent = (nowprogress + 1) * (100/total)
        print(" " + "[" + ">" + get_progress + "-" + get_pro + ']' + "%.2f" % percent + "%",end="")

    def creat_folder(self,path):
        from pathlib import Path

        try:
            #创建目录
            if Path(path).exists():
                warninglog(path + "is exists")
            else:
                os.makedirs(path)
                successlog("creat folder success:" + path)
            # 更改权限
            os.chmod(path, stat.S_IRWXU)
        except BaseException as error:
            warninglog(format(error))


if __name__ == "__main__":
    # File().uncompress_file()

    File().creat_folder("~/xycache/test")