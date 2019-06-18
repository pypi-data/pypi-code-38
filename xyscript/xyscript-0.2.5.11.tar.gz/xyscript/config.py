#!/usr/bin/env python
# coding=utf-8
#-*- encoding:utf-8 -*-
# from __future__ import print_function
import configparser, os, sys, re
from xyscript.xylog import logitem,warninglog
from xyscript.common.interaction import Interaction

#缓存文件存储路径
log_store_local = "/dist/" 

# root_dir = os.path.abspath('.')
dir = os.path.split(os.path.realpath(__file__))[0]
root_dir = os.path.abspath(os.path.join(dir,"."))
pro_dir = os.path.abspath(os.path.join(dir,".."))
cf = configparser.ConfigParser()
cf.read(root_dir + '/config.ini')
secs = cf.sections()

class Config:
    def get_version(self):
        global cf
        version = cf.get("Project-config", "version")
        return version
    
    def get_description(self):
        global cf
        description = cf.get("Project-config", "description")
        return description

    def get_long_desctription(self):
        global pro_dir
        long_des = open(os.path.join(pro_dir,'README.rst')).read()
        return long_des

    def get_file_store_path(self):
        global cf
        path = cf.get("File-store-path", "log_store_local")
        return path

    def get_sys_root_path(self):
        return os.path.expanduser('~')

    def get_config(self,kind,key):
        global cf
        path = cf.get(kind,key)
        return path
    
    def check_version(self):
        """ 检查版本号 """
        shell_str = "pip3 search xyscript"
        result = os.popen(shell_str)
        text = result.read()
        result = re.findall(r"xyscript \((.+?)\)",text)
        if len(result) == 1:
            local_version = self.get_version()
            remote_version = result[0]
            if local_version != remote_version:
                warninglog("################################################################################################")
                warninglog("# the latest version of xyscript is:" + remote_version + ", but yours is still:" + local_version)
                warninglog("# this will cause errors or some features will not work")
                warninglog("# you can use 'pip3 install xyscript -U' to update the latest version")
                warninglog("################################################################################################")
        

if __name__ == "__main__":
    # Config().check_version()
    print(Interaction().get_user_input("please enter password"))
    print(Config().get_sys_root_path())