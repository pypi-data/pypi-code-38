# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 00:52:07 2019

@author: Steven
"""

def debug(func):
    def wrapper():
        print( "[DEBUG]: enter {}()".format(func.__name__))
        return func()
    return wrapper

@debug
def say_hello():
    print("hello!")
    
say_hello()




def esql(st):
    def wrapper():
        return str(st)
    return wrapper

@
