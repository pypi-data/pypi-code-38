#-*- encoding:utf-8 -*-
import os, sys

class Common:
    def run_shellstring(self,shell_str):
        os.system(shell_str)
    
    def run_shellstring_forreslut(self,shell_str):
        os.system(shell_str)
        result = os.popen(shell_str)
        text = result.read()
        return text
        