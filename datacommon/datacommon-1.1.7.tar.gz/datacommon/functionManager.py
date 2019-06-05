# -*- coding: utf-8 -*-
# author: pengr


class FunctionManager:
    def __init__(self):
        print("初始化")
        self.functions = {}

    def executeFunc(self,func=None):
        print(self.functions)
 
    def register(self, func):
        self.functions[func.__name__] = func
 
 
fm = FunctionManager()
 
 
@fm.register
def t1():
    print("t1")
 
 
@fm.register
def t2():
    print("t2")
 
 
@fm.register
def t3():
    print("t3")
 
fm.execute_all()
fm.executeFunc()