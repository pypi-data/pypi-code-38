#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
from xyscript.xylog import warninglog

class Extension:
    def get_location_version(self):
        with open(os.path.dirname(os.path.realpath(__file__))+ "/config.py") as f:
            for line in f:
                if line.startswith('__version__'):
                    return eval(line.split('=')[-1])

    def get_current_version_des(self):
        with open(os.path.dirname(os.path.realpath(__file__))+ "/config.py") as f:
            for line in f:
                if line.startswith('__des__'):
                    return eval(line.split('=')[-1])

    def _search_lastest_version(self,bash_str):
        text = os.popen(bash_str)
        f = text.read()
        result = re.findall(".*xyscript \\((.*)\\).*",f)
        # print(len(result))
        if len(result) == 1:
            return result[0]
        else:
            return None

    def check_version(self):
        remote_version = Extension()._search_lastest_version("pip3 search xyscript")
        local_version = Extension().get_location_version()
        if remote_version is not None and remote_version != local_version :
            warninglog("the latest version of xyscript is: " + remote_version + ",but you are still in version: " + local_version)
            warninglog("this will cause many features to become unusable")
            warninglog("you can run 'sudo pip3 install xyscript -U' to update xyscript")
        # print(Exception()._search_lastest_version("pip3 search xyscript"))


if __name__ == "__main__":
    # Extension()._search_lastest_version("pip3 search xyscript")
    Extension().check_version()