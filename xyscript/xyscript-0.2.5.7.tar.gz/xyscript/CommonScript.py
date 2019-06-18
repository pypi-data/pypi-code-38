#!/usr/bin/env python
# coding=utf-8
# -*- encoding:utf-8 -*-
# from __future__ import print_function

import json

import os
import sys
import stat

from git import Repo

from xyscript.xylog import *
import xyscript.globalvar as gv

project_name = ''
branch_name = ''
platform = ''

project_repo = None
have_remove_pod_lockfile = False

PROJECTS = [
    {'name': "driver", 'url': ""},
    {'name': "passenger",
     'url': ""},
    {'name': "test", 'url': "git@github.com:littertwo/iosTestDemo.git"}
]


def package_project_with_enter(projects):
    global project_name, branch_name, platform
    url = ''
    for index, project in enumerate(projects):
        if project['name'] == project_name:
            # 拉取项目
            package_project(project)
            return

    if url == '':
        print("没有找到项目名为：", project_name, "的项目")

# def select_project_to_package(projects=None):
#     project_count = len(projects)

#     if project_count > 0 :
#         print("发现",project_count,"个可打包工程，请选择：")
#         for index ,project_objc in enumerate(projects):
#             print(index+1,")",project_objc['name'])
#         print(project_count+1,"）above all")

#         project_index = input("请输入要打包的工程:")
#         package_project_with_index(project_index,projects)
#     else:
#         print("当前不存在可以打包的项目")

# def package_project_with_index(project_index,projects):
#     try:
#         index = int(project_index)
#         # 索引值正确
#         if index >0 and index<len(projects)+1:
#             package_projectlist([projects[index-1]])
#         elif index == len(projects)+1:
#             package_projectlist(projects)
#         else:
#             reinput_index = input("索引值不存在，请重新输入:")
#             package_project_with_index(reinput_index,projects)
#         # print(index)
#     except ValueError:
#         reinput_index = input("索引值应该为数字，请重新输入:")
#         package_project_with_index(reinput_index,projects)


def package_projectlist(project_list):
    for project in project_list:
        package_project(project)


def package_project(project):
    print("开始打包名为：", project['name'], "的项目...")
    # 创建目录
    try:
        os.mkdir(project['name'])
        pass
    except IOError as error:
        print(format(error))
    else:
        # print(os.getcwd())
        pass
        project_path = os.getcwd() + "/" + project['name']
        print(project_path)
        gitLabTool = GitLabTool(project_path)
        repo = gitLabTool.clone_project(project['url'], project['name'])
        # gitLabTool.change_branch(repo)
        # print(os.getcwd())
        os.chdir(project_path)
        # 执行拉取子模块脚本
        project_tool = IOSProjectTool()
        project_tool.run_script('ProjConfig.py')
        project_tool.run_pod_install()
        project_tool.fastlane_to_package()


class IOSProjectTool:
    def run_script(self, path):
        print("执行脚本，路径是", path)
        shell_str = "python3 " + path
        print(os.system(shell_str))

    def have_podfile(self):
        filepath = os.getcwd() + '/Podfile'
        if os.path.exists(filepath):
            return True
        return False

    def run_pod_install(self,script=None,ispackage=None):
        global have_remove_pod_lockfile
        if script == None:
            script = "pod install"
        print("start run " + script)

        try:
            # r = os.popen(script)
            # r = Log().printandresult(script)
            text = printandresult(script)
            # print(text)
            result = "Pod installation complete!" not in text
            if result:
                faillog("run " + script +" failed")
                if script == "pod install" and not have_remove_pod_lockfile: 
                    self.run_pod_install("pod install --repo-update")
                elif not have_remove_pod_lockfile:
                    os.system("rm Podfile.lock")
                    have_remove_pod_lockfile = True
                    self.run_pod_install("pod install")
                else:
                    if ispackage:
                        pass
                        # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
                    sys.exit()
            # r.close()
            
        except BaseException:
            faillog("run " + script +" failed")
            if ispackage:
                pass
                # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
            sys.exit()

    def run_cert_syn(self):
        print("项目执行fastlane syn")
        shell_str = "fastlane syn"
        print(os.system(shell_str))

    def fastlane_to_package(self):
        global platform
        print("fastlane 自动打包")
        shell_str = "fastlane package" + platform
        print(os.system(shell_str))


class GitLabTool:
    # def __init__(self, local_path=None):
    #     # repo = Repo("git@github.com:littertwo/iosTestDemo.git")
    #     # self.repo = repo
    #     pass

    def test(self):
        print("test")

    # 克隆项目
    def clone_project(self, url, local_path):
        global project_repo
        try:
            # 更改权限
            os.chmod('./', stat.S_IRWXU)
            # 克隆仓库
            project_repo = Repo.clone_from(
                url=url, to_path=local_path, progress=None)
            # print(project_repo.create_head('branchname'))
        except IOError as error:
            print(format(error))
        else:
            print("克隆项目成功")
            return project_repo

    def pull_submodule(self):
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
                print(module_path + " " +
                      moduleConfig["branch"] + " pull success")
        except BaseException as error:
            print("拉取子模块失败", error)

    # 切换分支
    def change_branch_g(self, branch_name, git=None):
        if git is None:
            repo = Repo(os.getcwd())
            # print("branch_name:",branch_name)
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
                pass
                # print("就是当前分支，不需要切换")
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

                        repo.head.reference = local_target_branch
                    except BaseException as error:
                        errstr = "\033[1;31m" + "切换分支失败：" + str(error) + "\033[0m"
                        print(errstr)
                        sys.exit()
                    
                else:
                    remote_branch_name = 'origin/' + branch_name
                    if remote_branch_name in remote_branch_names:
                        # print("远端存在目标分支同名分支，checkout")
                        try:
                            git = repo.git
                            git.checkout('-b', branch_name, remote_branch_name)
                            # repo.remote().pull()
                            # print("切换分支成功")
                        except BaseException as error:
                            errstr = "\033[1;31m" + "checkout分支失败：" + str(error) + "\033[0m"
                            print(errstr)
                    else:
                        errstr = "\033[1;31m" + "远端不存在名为："+ branch_name + "的分支，无法checkout,请先创建远端仓库分支再checkout" + "\033[0m"
                        print(errstr)

        else:
            print(branch_name)

    def get_all_projects(self):
        print(PROJECTS)


# parm1：项目名称 parm2：分支名称 parm3：打包的平台
def main(argv):
    global project_name, branch_name, platform

    project_name = argv[1]
    branch_name = argv[2]
    platform = argv[3]

    print('开始打包....')

    # gitLabTool = GitLabTool("")
    # projects = gitLabTool.get_all_projects()
    # select_project_to_package(projects)
    package_project_with_enter(PROJECTS)


if __name__ == "__main__":
    print('开始执行脚本.....')
    # main(sys.argv)
    # print(IOSProjectTool()._have_podfile())
