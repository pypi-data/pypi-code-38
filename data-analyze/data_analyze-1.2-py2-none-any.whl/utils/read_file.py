# -*- coding: utf-8 -*-
# 根据传入数据和规则进行结果分析
# chang.lu

import os

def read_file_data(file_path):
    """读取文件数据"""
    if not os.path.exists(file_path):
        print('ERROR XXXXXXXXX  读取文件不存在', file_path)
        return None
    else:
        with open(file=file_path, mode='r', errors='ignore') as f:
            content = f.read()
            f.close()
            return str(content)