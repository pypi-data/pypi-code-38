#!/usr/bin/env python
# coding=utf-8
#-*- encoding:utf-8 -*-
# from __future__ import print_function

__version__ = '0.2.4.5'
__des__     = 'added version checking function at the end of each execution\nupload to pgyer with different env'

#缓存文件存储路径
log_store_local = "/dist/" 

class Config:
    def get(self,project):
        print(project)
        # pass
    def get_version(self):
        return __version__
        
