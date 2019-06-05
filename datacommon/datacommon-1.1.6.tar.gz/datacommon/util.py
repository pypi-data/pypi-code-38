# -*- coding: utf-8 -*-
# author: pengr


import chardet
import codecs

# Null bytes; no need to recreate these on each call to guess_json_utf
_null = '\x00'.encode('ascii')  # encoding to ASCII for Python 3
_null2 = _null * 2
_null3 = _null * 3


def guessTextEncode(text):
    """
    :rtype: str
    """
    res = chardet.detect(text)["encoding"]
    if res:
        return res
    sample = text[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return 'utf-32'     # BOM included
    if sample[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'  # BOM included, MS style (discouraged)
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return 'utf-16'     # BOM included
    nullcount = sample.count(_null)
    if nullcount == 0:
        return 'utf-8'
    if nullcount == 2:
        if sample[::2] == _null2:   # 1st and 3rd are null
            return 'utf-16-be'
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return 'utf-16-le'
        # Did not detect 2 valid UTF-16 ascii-range characters
    if nullcount == 3:
        if sample[:3] == _null3:
            return 'utf-32-be'
        if sample[1:] == _null3:
            return 'utf-32-le'
        # Did not detect a valid UTF-32 ascii-range character
    return None



import os

# 根据数据集建立目录
def saveContent(path, content):
    if os.path.exists(path):
        return
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(path, 'wb') as f:
        f.write(content)

# 罗列文件
def listFile(dir='source'):
    # 读取source文件夹下所有文件
    # @param: str
    file_list = []
    for root, _, files in os.walk(dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


# 判断空数据
def isBlank(item, NonKeys=['NONE', 'NULL', 'NON']):
    if item is None or len(str(item)) == 0 or str(item).strip().upper() in NonKeys:
        return True
    for ch in str(item):
        if ch != ' ':
            return False
    return True

# 统计非法日期格式格式数据条目/所占比


import time

# 判断日期格式


def isDateTrueFormat(date, format='%Y-%m-%d'):
    try:
        time.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False


# 通过类名获取对象
def createInstance(module_name, class_name, *args, **kwargs):
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj