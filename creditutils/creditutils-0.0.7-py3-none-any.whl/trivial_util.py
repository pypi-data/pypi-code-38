# -*- coding:UTF-8 -*-


'''
Created on 2013-8-7

@author: caifenghua
'''

import codecs
import json
import datetime
import time
import creditutils.str_util as str_utils


def filter_unique_item(items):
    dst_items = []
    for item in items:
        item_same = None
        for item_in in dst_items:
            if item == item_in:
                item_same = item
                break

        if item_same != None:
            print(item_same)
        else:
            dst_items.append(item)

    return dst_items


def decode_to_unicode(string):
    import chardet
    result = chardet.detect(string)
    return codecs.decode(string, result['encoding'])


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def measure_time(func, *args, **dicts):
    begin = time.time()

    func(*args, **dicts)

    end = time.time()
    time_info = str_utils.get_time_info(begin, end)

    # 输出总用时
    print('===Finished. Total time: {}==='.format(time_info))


if __name__ == '__main__':
    #     string = '我们的祖国像花园'
    #     result = chardet.detect(string)
    #     print(result)
    #
    #     decode_to_unicode(string)

    print('to the end')
