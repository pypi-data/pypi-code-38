#!/usr/bin/env python
# coding=utf-8
#-*- encoding:utf-8 -*-
# from __future__ import print_function
import os, sys
import json

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from git import Repo

def pullsubmodules():
    try:
        currentPath = os.getcwd()
        repo = Repo(currentPath)
        initFlag = 0
        file = open("ProjConfig.json")
        moduleConfigList = json.load(file)
        for moduleConfig in moduleConfigList:
            module_path = currentPath + "/" + moduleConfig["module"]
            if not os.listdir(module_path):
                initFlag = 1
        if initFlag == 1:
            print("submodule init...")
            repo.git.submodule('update', '--init')
            print("submodule init success")
        for moduleConfig in moduleConfigList:
            module_path = currentPath + "/" + moduleConfig["module"]
            sub_repo = Repo(module_path)
            sub_remote = sub_repo.remote()
            sub_repo.git.reset('--hard')
            sub_repo.git.checkout(moduleConfig["branch"])
            sub_remote.pull()
            print(module_path + " " + moduleConfig["branch"] + " pull success")
    except BaseException as error:
        print("拉取子模块失败", error)

    
    
