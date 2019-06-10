#-*- encoding:utf-8 -*-
import os, sys, re
from xyscript.xylog import logitem,warninglog
from xyscript.common import Common

class Extension:
    def get_current_version_des(self,fname=os.path.join('xyscript', 'config.py')):
        """ 当前版本描述 """
        with open(fname) as f:
            for line in f:
                if line.startswith('__des__'):
                    return eval(line.split('=')[-1])

    def get_location_version(self,fname=os.path.join('xyscript', 'config.py')):
        """ 当前本地版本号 """
        with open(fname) as f:
            for line in f:
                if line.startswith('__version__'):
                    return eval(line.split('=')[-1])

    def check_version(self):
        """ 检查版本号 """
        shell_str = "pip3 search xyscript"
        result = os.popen(shell_str)
        text = result.read()
        result = re.findall(r"xyscript \((.+?)\)",text)
        if len(result) == 1:
            local_version = self.get_location_version()
            remote_version = result[0]
            if local_version != remote_version:
                warninglog("################################################################################################")
                warninglog("# the latest version of xyscript is:" + remote_version + ", but yours is still:" + local_version)
                warninglog("# this will cause errors or some features will not work")
                warninglog("# you can use 'pip3 install xyscript -U' to update the latest version")
                warninglog("################################################################################################")



if __name__ == "__main__":
    # print(Extension().get_current_version_des())
    # print(Extension().get_location_version())
    Extension().check_version()