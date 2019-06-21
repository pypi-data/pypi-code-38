# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/9/5 0005
__author__ = 'huohuo'
a = ['1','2','3','4']
b = ['1','2','3']
c = ['1','5','6','2','3','7']
a1 = ','.join(a)
b1 = ','.join(b)
if b1 in a1:
    a1 = a1.replace(b1, ','.join(c))
    a = a1.split(',')
    print 'a = ', a
    print 'b = ', b
    print 'c = ', c
    print '=====after======'
    print 'a = ', a
if __name__ == "__main__":
    pass
    

