# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/7/5 0005
__author__ = 'huohuo'
import os
if __name__ == "__main__":
    pass
    

def get_imgs(path):
    for i in os.listdir(path):
        path_file = os.path.join(path,i)
        if os.path.isfile(path_file):
            path_file1 = path_file.replace(' ', '_')
            os.rename(path_file, path_file1)
        else:
            get_imgs(path_file)


get_imgs('D:\pythonproject\\report\data')