import sys
import math
import time
import codecs
from collections import Iterable


def readfile(file, encoding='utf8'):
    """
    读取文本文件, 返回文本文件内容
    :param file: 要读取的文件名
    :param encoding: 文件编码, 默认为utf8
    :return: 返回文件内容
    """
    with codecs.open(file, mode='r', encoding=encoding) as f:
        return f.read()


def writefile(file, content, mode='w', encoding='utf8'):
    """
    将文本内容写入文件
    :param file: 要写入的文件名
    :param content: 要写入的内容
    :param mode: 写入模式, 默认为w覆盖
    :param encoding: 写入编码, 默认为utf8
    :return:
    """
    with codecs.open(file, mode=mode, encoding=encoding) as f:
        f.write(content)


def transcode(from_file, to_file, from_code='utf8', to_code='GBK'):
    """
    转换文本文件格式
    :param from_file: 待转换的文件名
    :param to_file: 转换后的文件名
    :param from_code: 转换前的文件编码
    :param to_code: 转换后的文件编码
    :return:
    """
    content = readfile(from_file, encoding=from_code)
    writefile(to_file, content, encoding=to_code)
    return '{} ====> {}'.format(from_file, to_file)


def split_list(li, num=8):
    """
    分割列表
    :param li: 要分割的列表
    :param num: 要分割的份数
    :return: 返回分割结果
    """
    return split_list_by_len(li, math.ceil(len(li) / num))


def split_list_by_len(li, n):
    return [li[i: i + n] for i in range(0, len(li), n)]


class WithProgressBar(object):
    """
    用于在控制台打印一个进度条，用法（作用于for 循环）：
        # 仅打印进度条
        for i in WithProgressBar(range(1000)):
           pass
        ##############################################----98%

        # 打印进度条，并获得一部分预览数据
        preview_data = PreviewDataInBar()
        for i in WithProgressBar(range(1000), preview_data=preview_data):
            pass
        ##################################################100%
        print(preview_data.preview)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,... ...199]
    """
    def __init__(self, iterable: Iterable, sign: str='#', preview_data=None, condition=lambda obj: True):
        """
        传入一个可迭代对象iterable， 传入一个条件condition，yield 满足条件的元素。
        在这个过程中，会在控制台打印一个进度条，进度条符号用sign表示。
        如果传入了preview_data（一个PreviewDataInLoop 的实例），会截取一部分元素作为预览数据。
        :param iterable:
        :param sign:
        :param preview_data:
        :param condition:
        """
        if isinstance(iterable, Iterable):
            self.iterable = iterable
        elif isinstance(iterable, int):
            self.iterable = range(iterable)
        else:
            raise TypeError
        self.sign = sign
        self.preview_data = preview_data
        self.count = 0
        self.condition = condition

    def __len__(self):
        return len(self.iterable)

    def __iter__(self):
        i = 0
        for i, obj in enumerate(self.iterable, 1):
            if self.condition(obj):
                if isinstance(self.preview_data, PreviewDataInLoop):
                    self.preview_data.append(obj)
                    # self.preview_data.count += 1
                    # if self.preview_data.count <= self.preview_data.limit:
                    #     self.preview_data.preview.append(obj)
                yield obj

            percentage = i * 100 / self.__len__()
            time_now = time.strftime('%Y-%m-%d %H:%M:%S>')

            writing = time_now + self.sign * int(percentage / 2) + '-' * (50 - int(percentage / 2)) + '%d%%\r' % (percentage)
            sys.stdout.write(writing)
            sys.stdout.flush()
        sys.stdout.write(time_now + self.sign * 50 + '100%\r\n')
        self.count = i


class PreviewDataInLoop(object):
    """
    用于获取for 循环中的预览数据，用法见于WithProgressBar类的注释信息，也可见于以下信息：
        preview_data = PreviewDataInBar()
        for i in preview_data.with_progress_bar(range(1000)):
            time.sleep(0.1)

        ##################################################100%
        print(preview_data.preview)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,... ...199]

    为什么要在for循环中取一部分预览数据？——这在数据库取数据中有用。
    如何作用于while 循环？没什么特别好的方法。
        preview_data = PreviewDataInBar()
        while some_condition(obj):
            preview_data.append(obj)
    """
    def __init__(self, limit=200):

        self.preview = []
        self.limit = limit
        self.count = 0

    def append(self, obj):
        self.count += 1
        if self.count <= self.limit:
            self.preview.append(obj)

    def with_progress_bar(self, iterable, sign='#', condition=lambda obj: True):
        return WithProgressBar(iterable=iterable, sign=sign, preview_data=self, condition=condition)


