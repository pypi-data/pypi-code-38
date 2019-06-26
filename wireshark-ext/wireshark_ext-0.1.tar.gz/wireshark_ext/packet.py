#!/usr/bin/env python
#coding:utf-8
"""
  Author:  cat --<yafeile@sohu.com>
  Purpose: Wiresark数据包转换
  Created: 2019/6/26
"""
from __future__ import unicode_literals, print_function
import six

def copy_from_wireshark(raw):
    """
    Copy Hexadecimal from WireShark 
    """
    result = []
    if six.PY3:
        flag = ''
    else:
        flag = b''
    for r in raw.split('\n'):
        line = []
        for x in r.split():
            l = len(x)
            if l == 2:
                x = chr(int(x, 16))
                line.append(x)
        _line = flag.join(line)
        result.append(_line)
    if six.PY3:
        return flag.join(result).encode("utf-8")
    return flag.join(result)


def convert_to_wireshark(raw,step=16):
    """
    Convert Hexadecimal to Wireshark format
    """
    arr = list(map(ord, raw))
    l = len(arr)
    result = []
    for i in range(0, l, step):
        val = arr[i:i+step]
        line = []
        for v in val:
            v = hex(v)[2:].zfill(2)
            line.append(v)
        _line = ' '.join(line)
        _line = '{}  {}'.format(hex(i)[2:].zfill(4), _line)
        result.append(_line)
    return '\n'.join(result)

def test():
    raw = """0000   10 32 81 80 00 01 00 01 00 00 00 00 06 67 6f 6f
0010   67 6c 65 03 63 6f 6d 00 00 10 00 01 c0 0c 00 10
0020   00 01 00 00 01 0e 00 10 0f 76 3d 73 70 66 31 20
0030   70 74 72 20 3f 61 6c 6c"""
    val = copy_from_wireshark(raw)
    print(repr(val))
    val = convert_to_wireshark(val)
    print(val)

if __name__ == '__main__':
    test()