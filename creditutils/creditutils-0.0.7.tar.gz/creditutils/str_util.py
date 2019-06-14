# -*- coding:UTF-8 -*-

'''
Created on 2014年12月5日

@author: caifh
'''

# import chardet.universaldetector as det_
import creditutils.system_util as mysystem
import chardet


def escape_entire(src):
    ch = (ord(c) for c in src)
    return ''.join(('\\x%02x' % c) if c <= 255 else ('\\u%04x' % c) for c in ch)


# 将字符串转换成bool类型
def get_bool(value):
    return str(value).lower() == str(True).lower()


def escape(src):
    return ascii(src)[1:-1]


def decode_escape(src):
    return '{}'.format(bytes(src, 'ascii').decode('unicode-escape'))


def detect_encoding(src_buf, default_encoding=None):
    enc_flag = 'encoding'

    # 复杂处理
    #     detector = det_.UniversalDetector()
    #
    #     detector.feed(src_buf)
    #     if detector.done:
    #         encoding = detector.result[enc_flag]
    #
    #     detector.close()
    #     print(detector.result)

    # 简化实现
    result = chardet.detect(src_buf)
    #     print(result)

    encoding = result[enc_flag]
    if not encoding:
        if default_encoding:
            encoding = default_encoding
        else:
            encoding = mysystem.get_system_encoding()

        #     print('encoding: ' + encoding)

    return encoding


def decode_to_unicode(src_buf):
    encoding = detect_encoding(src_buf)

    rtn_str = ''
    if src_buf:
        rtn_str = src_buf.decode(encoding)

    return rtn_str


# 获取以秒为单位的两个时间点之间的差值，返回以XXmXXs的时间格式字符串
def get_time_info(begin, end):
    elapsed = end - begin
    sec_per_min = 60
    m = elapsed // sec_per_min
    s = elapsed % sec_per_min
    time_info = '{}m{}s'.format(round(m), round(s))
    return time_info
