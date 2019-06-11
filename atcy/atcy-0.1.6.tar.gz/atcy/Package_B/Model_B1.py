# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""Model B1 doc"""

b1=400
def div(x,y):
    """
    Div function doc...
    """
    return x/y

class B:
    """
    class doc...x,y;get_x,set_x,show
    """
    def __init__(self,x,y):
        self.x=x;self.y=y
    def get_x(self):
        """
        get_x doc...
        """
        return self.x
    def set_x(self,x):
        self.x=x

    def show(self):
        print('x=',self.x,'y=',self.y)

