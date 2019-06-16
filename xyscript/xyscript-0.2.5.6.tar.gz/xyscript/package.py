#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import stat
import time
import threading
import time

from git import Repo

from xyscript.xylog import *
from xyscript.cert import Cert
from xyscript.CommonScript import IOSProjectTool
from xyscript.mail import Email
import xyscript.globalvar as gv
from xyscript.iosProjectTool import IOSTool



SELECT_FILE_COUNT = 0
WORK_SPACE = None

ENV_CHANGE_COUNT = 0


class Package:
    
    def clone_form_address(self,address,local_path):

        from pathlib import Path
        folder_name = (address.split("/")[-1]).split(".")[0] +' ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        try:
            #创建目录
            local_path = local_path + "/" + folder_name
            if Path(local_path).exists():
                warninglog(folder_name + "is exists")
            else:
                os.mkdir(local_path)
            
            try:
                os.chdir(local_path)
                warninglog("current workspace is: " + local_path)
            except BaseException as error:
                faillog("change worksapce failed")
                # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
                sys.exit()
                
            # 更改权限
            os.chmod(local_path, stat.S_IRWXU)
            local_path = local_path + "/"
            Repo.clone_from(url=address, to_path=local_path, progress=None)
            successlog("clone project success")
        except BaseException as error:
            warninglog(format(error))

    def change_branch(self, branch_name, git=None):
        """
        change_branch
        """
        if git is None:
            repo = Repo(os.getcwd())
            # print(os.getcwd())
            print("start change branch to:",branch_name)
            local_branch_names = []#本地库列表
            remote_branch_names = []#远端库列表
            current_branch = repo.active_branch.name
            # print("current_branch_name:", current_branch)
            for localitem in repo.heads :
                local_branch_names.append(localitem.name)
                # print(localitem.name)
            # print("local_branch_names:", local_branch_names)

            for remoteitem in repo.refs:
                remote_branch_names.append(remoteitem.name)
                # print(remoteitem)
            # print("remote_branch_names:", remote_branch_names)

            if branch_name == current_branch:
                # print("就是当前分支，不需要切换")
                warningstring = "current branch is already :" + branch_name
                warninglog(warningstring)
            else:
                if branch_name in local_branch_names:
                    # print("本地存在目标分支，切换即可")
                    try:
                        local_target_branch = None
                        if branch_name == "develop":
                            local_target_branch = repo.heads.develop
                        elif branch_name == "Develop" :
                            local_target_branch = repo.heads.Develop
                        elif branch_name == "master" :
                            local_target_branch = repo.heads.master
                        else:
                            local_target_branch = repo.heads[branch_name]

                        repo.head.reference = local_target_branch
                        successlog("change branch success")
                    except BaseException as error:
                        errstr = "change branch failed:" + str(error)
                        faillog(errstr)
                        # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
                        sys.exit()
                    
                else:
                    remote_branch_name = 'origin/' + branch_name
                    if remote_branch_name in remote_branch_names:
                        # print("远端存在目标分支同名分支，checkout")
                        try:
                            git = repo.git
                            git.checkout('-b', branch_name, remote_branch_name)
                            # repo.remote().pull()
                            successlog("change branch success")
                        except BaseException as error:
                            errstr = "checkout failed:" + str(error)
                            faillog(errstr)
                    else:
                        errstr = "have no branch named:" + branch_name + " exist,cannot to checkout"
                        # errstr = "\033[1;31m" + "远端不存在名为："+ branch_name + "的分支，无法checkout,请先创建远端仓库分支再checkout" + "\033[0m"
                        faillog(errstr)
                        # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
                        sys.exit()

        else:
            print(branch_name)

    def pull_submodule(self):
        """
        pull submodules
        """
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
                successlog("submodule init success")
            for moduleConfig in moduleConfigList:
                module_path = currentPath + "/" + moduleConfig["module"]
                sub_repo = Repo(module_path)
                sub_remote = sub_repo.remote()
                sub_repo.git.reset('--hard')

                branch = ""
                bracnh_name = ""
                if "branch" in moduleConfig.keys():
                    branch = "\tbranch"
                    bracnh_name = "\t" + moduleConfig["branch"]
                    sub_repo.git.checkout(moduleConfig["branch"])
                elif "commit" in moduleConfig.keys():
                    branch = "\tcommit"
                    bracnh_name = "\t" + moduleConfig["commit"]
                    sub_repo.git.checkout(moduleConfig["commit"])
                elif "tag" in moduleConfig.keys():
                    branch = "\ttag"
                    bracnh_name = "\t" + moduleConfig["tag"]
                    sub_repo.git.checkout(moduleConfig["tag"])
                sub_remote.pull()
                string = "\t" + moduleConfig["module"] + logitem().successitem(bracnh_name) + " of " + logitem().successitem(branch) + " \tpull success"
                print(string)

        except BaseException as error:
            errorstr = "pull submodule failed:" + format(error)
            faillog(errorstr)
            # sys.exit()
    
    def change_default_net_env(self,env):
        global ENV_CHANGE_COUNT
        filepath = self._search_xcodeproj() + "/project.pbxproj"
        print("start change default environment variable")
        file_data = ""
        try:
            with open(filepath,encoding="utf-8") as f:
                for line in f:
                    if "SC_URL_TYPE =" in line:
                        print(line,end="")
                        line = str.split(line,'SC_URL_TYPE')[0] + "SC_URL_TYPE = " + env +";\n"
                    file_data += line

            with open(filepath,"w",encoding="utf-8") as f:
                f.write(file_data)
            successlog("change " + env +" environment success")   
        except BaseException  as error:
            faillog("change " + env +" environment failed:" + format(error))
        
    def _just_for_uploadbugly(self):
        filepath = self._search_xcodeproj() + "/project.pbxproj"
        print("start add build setting for upload bugly")
        file_data = ""
        try:
            with open(filepath,encoding="utf-8") as f:
                for line in f:
                    add_line = ""
                    if "SC_URL_TYPE =" in line:
                        add_line = str.split(line,'SC_URL_TYPE')[0] + "SC_BUGLY_DEFAULT = default;\n"
                    file_data += line 
                    file_data += add_line
            with open(filepath,"w",encoding="utf-8") as f:
                f.write(file_data) 
            successlog("add build setting for upload bugly success")
        except BaseException  as error:
            faillog("add build setting for upload bugly failed:" + format(error))

        
    def _search_xcodeproj(self):
        paths = os.listdir(os.getcwd())
        for filename in paths:
            if ".xcodeproj" in filename :
                return filename
        faillog("The current path does not have a: xcodeproj file,such as :projectname.xcodeproj")
        # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
        sys.exit()

    def select_directory(self):
        global SELECT_FILE_COUNT

        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.update()
        file_path = filedialog.askdirectory(initialdir=os.getcwd(), title="选择项目存储的路径")

        SELECT_FILE_COUNT = SELECT_FILE_COUNT + 1
        if SELECT_FILE_COUNT >=3:
            faillog("you have give up choosing an folder three times!")
            # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
            sys.exit()
        if file_path == "":
            warninglog("please choose an folder")
            self.select_directory()
        else:
            root.update()
            # root.mainloop()
            return file_path

    def _add_empty_file(self,fileName="package_empty_file"):
        f= open(fileName,"w")
        f.close
    
    def _platform_package(self,shell_str):
        text = printandresult(shell_str)
        if "fastlane.tools just saved" in text or "fastlane.tools finished successfully" in text:
            return True
        else:
            return False
    
    def _pull_lastest_code(self,branch):
        currentPath = os.getcwd()
        repo = Repo(currentPath)
        repo.git.checkout(branch)
        file = open("ProjConfig.json")
        moduleConfigList = json.load(file)
        print("pull " + logitem().successitem("shell") + " in branch " + logitem().successitem(branch) + " success")
        repo.git.pull()
        for moduleConfig in moduleConfigList:
            module_path = currentPath + "/" + moduleConfig["module"]
            sub_repo = Repo(module_path)
            sub_repo.git.checkout(moduleConfig["branch"])
            sub_repo.git.pull()
            print("pull " + logitem().successitem(moduleConfig["module"]) + " in shell " + logitem().successitem(branch) + " success")

    def _get_current_config_file(self):
        file = open("ProjConfig.json")
        moduleConfigList = json.load(file)
        return moduleConfigList

    def _clear_local_workspace(self,date):
        currentPath = os.getcwd()
        repo = Repo(currentPath)
        repo.git.reset('--hard')#清空壳工程本地工作空间
        for moduleConfig in date:
            module_path = currentPath + "/" + moduleConfig["module"]
            sub_repo = Repo(module_path)
            sub_repo.git.reset('--hard')
        print(logitem().successitem("clear local workspace success"))

    def add_tag_after_package(self,tag):
        try:
            if tag is not None:
                currentPath = os.getcwd()
                repo = Repo(currentPath)
                if tag not in repo.git.tag():
                    repo.git.tag(tag)
                    repo.git.push('origin',tag)
                    successlog("add tag to shell success")
                    #子模块添加tag
                    currentPath = os.getcwd()
                    file = open("ProjConfig.json")
                    moduleConfigList = json.load(file)
                    for moduleConfig in moduleConfigList:
                        module_path = currentPath + "/" + moduleConfig["module"]
                        sub_module = Repo(module_path)
                        sub_module.git.tag(tag)
                        sub_module.git.push('origin',tag)
                        successlog("add tag to " + moduleConfig["module"] + " success")
                else:
                    warninglog("tag named: " + tag + " is exists!")
        except BaseException as error:
            faillog("add tag failed:" + format(error))

    def handle_package_order(self,order_array=None,project_version=None, project_build=None, env=None):
        failed_platform = []
        for index, platform_name in enumerate(order_array):
            shell_str = "fastlane package" + platform_name + project_version + project_build + env
            result = self._platform_package(shell_str)
            if index != len(order_array) -1:
                IOSTool().add_content_to_file("AppDelegate.h")
            if result == False:
                failed_platform.append(platform_name)
        
        if len(failed_platform) > 0:
            faillog("package to all failed")
        else:
            successlog("package to all success")

    
    def package_to_platform(self,platform=None, project_version=None, project_build=None, emails=None, env=None,package_order=None):
        """
        配置证书 等效于 fastlane + platform
        """
        #获取项目当前version、build

        if platform == None:
            platform = "pgyer"
            
        version_str = ""
        build_str = ""
        env_str = ""
        if project_version != None:
            version_str = " version:" + project_version
        
        if project_build != None:
            build_str = " build:" + project_build

        if env != None:
            env_str = " env:" + env

        
        print("start package to " + platform)
        if Cert().fastlane_is_in_gem() or Cert().fastlane_is_in_brew() :
            shell_str = "fastlane package" + platform + version_str + build_str + env_str
            try:
                if Cert()._have_fastfile():
                    if platform == "all":#分开打包防止多次打包结果相互影响

                        if package_order == None or package_order == "0":
                            self.handle_package_order(["testflight","pgyer"],version_str,build_str,env_str)
                        elif package_order == "1":
                            self.handle_package_order(["pgyer","testflight"],version_str,build_str,env_str)
                        else:
                            faillog("nonsupport package_order")
                    else:
                        result = self._platform_package(shell_str)
                        if result:
                            successlog("package to " + platform + " success")
                        else:
                            faillog("package to " + platform + " failed")

                else:
                    faillog("You may not have the fastfile,please set fastlane up first!")
                    sys.exit()
                
            except BaseException  as error:
                faillog(str(error))
                sys.exit()
        else:
            warninglog("You may not have the fastlane installed yet,autoinstall now...")
            Cert()._install_fastlane()
            self.package_to_platform(platform,project_version,project_build,env=env)
    

    def auto_package(self, project_address=None, branch_name=None, platform=None, net_env=None, project_version=None, project_build=None,emails=None,tag_name=None,package_order=None):
        if branch_name == None:
            branch_name = "Develop"
        if platform == None:
            platform = "pgyer"
        if emails == None:
            emails = []

        print("自动打包\n项目：",project_address,"\n分支为：",branch_name,"\n发布平台为：",platform,"\n网络环境：",net_env,"\n版本号：",project_version,"\n编译号：",project_build)
        # print("please choose an folder")
        
        # #clone
        # self.clone_form_address(project_address,self.select_directory())
        self.clone_form_address(project_address,os.getcwd())
        # #切换分支
        self.change_branch(branch_name)
        # #拉子模块
        self.pull_submodule()
        # #pod indtall
        IOSProjectTool().run_pod_install()
        # #选择网络环境
        if net_env != None:
            self.change_default_net_env(net_env)
        # #fastlane syn
        # Cert().run_cert_syn()
        # #安装 pgyer 插件
        os.system("bundle install")
        # #打包
        self.package_to_platform(platform, project_version, project_build,emails,env=net_env,package_order=package_order)
        # 打tag
        self.add_tag_after_package(tag_name)

    def merge_code(self,code_branch,package_branch):
        """
        合并代码(开发分支名、打包分支名)
        """
        if code_branch == None:
            code_branch = "Develop"
        if package_branch == None:
            package_branch = "zuche-test"

        try:
            # os.chdir("/Users/sunweiwei/Desktop/Saic/ios-shell-driver")
            self.change_branch(code_branch)
            currentPath = os.getcwd()
            repo = Repo(currentPath)
            moduleConfigList = self._get_current_config_file()
            # 清空本地工作空间
            self._clear_local_workspace(moduleConfigList)
            # 检出 code_branch 分支的最新代码
            self._pull_lastest_code(code_branch)
            codebranch_config = self._get_current_config_file()
            # 检出 package_branch 分支的最新代码
            self._pull_lastest_code(package_branch)
            # 合并 code_branch 分支到当前 package_branch 分支
            for moduleConfig in codebranch_config:
                module_path = currentPath + "/" + moduleConfig["module"]
                sub_repo = Repo(module_path)
                merge_str = "Merge " + moduleConfig["branch"] + " into " + package_branch
                sub_repo.git.merge(moduleConfig["branch"],'-m', merge_str, '--log=10')
                print("merge " + logitem().successitem(moduleConfig["module"]) + " success")
            repo = Repo(currentPath)
            merge_str = "Merge " + code_branch + " into " + package_branch
            repo.git.merge(code_branch, '-m', merge_str ,'--log=10')
            print("Merge "+ logitem().successitem("shell") + " from " + logitem().successitem(code_branch) + " to " + logitem().successitem(package_branch) + " success")
            # repo.git.commit('-a', '-m', merge_str)

            #推远端
            repo.git.push()
            print("push " + logitem().successitem("shell") + " success")
            date = self._get_current_config_file()
            for moduleConfig in date:
                module_path = currentPath + "/" + moduleConfig["module"]
                sub_repo = Repo(module_path)
                sub_repo.git.push()
                print("push " + logitem().successitem(moduleConfig["module"]) + " success")

        except BaseException as error:
            errorstr = "pull submodule failed:" + format(error)
            faillog(errorstr)
            # sys.exit()


    def init_project(self, project_address=None, branch_name=None, platform=None, net_env=None):
        if branch_name == None:
            branch_name = "Develop"
        if platform == None:
            platform = "pgyer"

        print("initial 项目：",project_address," 分支为：",branch_name," 发布平台为：",platform,"网络环境：",net_env)
        print("please choose an folder")
        
        # #clone
        self.clone_form_address(project_address,self.select_directory())
        # #切换分支
        self.change_branch(branch_name)
        # #拉子模块
        self.pull_submodule()
        # #pod indtall
        IOSProjectTool().run_pod_install()
        # #选择网络环境
        if net_env != None:
            self.change_default_net_env(net_env)
        # #fastlane syn
        Cert().run_cert_syn()

if __name__ == "__main__":
    pass
    # Package().change_default_net_env("dev")
    # Package()._get_project_version()
    # Package().merge_code("Develop","zuche-test")
    # Package()._add_empty_file()
    # Package()._just_for_uploadbugly()
    # Package().auto_package("https://gitlab.saicmobility.com/saic-app-car-ios/ios-shell-driver.git","zuche-test","all","sit","1.0.0","1394") 
    # Package().pull_submodule()
    # IOSTool().add_content_to_file("AppDelegate.h")
    Package().add_tag_after_package("tag_03")