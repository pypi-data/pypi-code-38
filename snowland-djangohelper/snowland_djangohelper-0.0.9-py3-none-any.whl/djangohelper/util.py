#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: util.py
# @time: 2018/7/23 14:46
# @Software: PyCharm

import glob
import os
import re


def create_admin(modelname='models.py', adminname='admin_new.py', list_per_page=10, encoding='utf8'):
    """
    根据models生成admin
    :param modelname:
    :param adminname:
    :param list_per_page:
    :param encoding:
    :return:
    """
    lines = []
    with open(modelname, "r", encoding=encoding) as f:
        lines = f.readlines()
    items = []
    classnames = []
    with open(adminname, "w+", encoding=encoding) as f:
        f.write("from django.contrib import admin\n")
        f.write("from . import models\n\n")
        for eachline in lines:
            eachline = eachline.split('#')[0]

            if eachline.startswith("class"):
                if items:
                    f.write("    list_display = ('id',")
                    [f.write(" '" + item + "',") for item in items]
                    f.write(')\n')
                    f.write("    list_editable = (")
                    [f.write("'" + item + "',") for item in items]
                    f.write(')\n')
                    f.write('    list_per_page = ' + str(list_per_page) + "\n\n")
                items = []
                classname = eachline.split('(')[0][6:]
                classnames.append(classname)
                f.write('class ' + classname + 'Admin(admin.ModelAdmin):\n')
            elif eachline.find('=') > 0:
                splited = eachline.split('=')
                item = splited[0].replace(' ', '')
                if item != '' and item != "\n":
                    items.append(item)

        if items:
            f.write("    list_display = ('id',")
            [f.write(" '" + item + "',") for item in items]
            f.write(')\n')
            f.write("    list_editable = (")
            [f.write(" '" + item + "',") for item in items]
            f.write(')\n')

        f.write("\n\n")
        [f.write("admin.site.register(models." + classname + ", " + classname + "Admin)\n") for classname in classnames]


trans_list = ['.html', '.htm']


def trans_file(file, encoding='utf-8'):
    splitext = os.path.splitext(file)
    with open(file, "r", encoding=encoding) as f1, open("{}.bak".format(splitext[0]), "w", encoding=encoding) as f2:
        for line in f1:
            if "<title>" in line:
                f2.write("{% load staticfiles %}\n")
            n_line = trans_href(line)
            n_line = trans_src(n_line)
            f2.write(n_line)

    os.remove(file)
    os.rename("{}.bak".format(splitext[0]), file)


def trans_href(s):
    pattern_href = re.compile('href=[\"|\'].*?\.css[\"|\']')
    str_href = re.findall(pattern_href, s)
    if str_href and not (str(str_href).startswith('http')):
        str_href = str_href[0][6:-1]
        s = s.replace(str_href, "{%static '" + str_href + "'%}")
    return s


def trans_src(s):
    pattern_src = re.compile('src=".*?[\.js|\.css|\.png\.jpg|\.bmp|\.gif]"')
    str_src = re.findall(pattern_src, s)
    if str_src and (not str(str_src).startswith('http')):
        str_src = str_src[0][5:-1]
        s = s.replace(str_src, "{%static '" + str_src + "'%}")
    return s


def trans(root, encoding="utf-8"):
    files = [root + '/' + i for i in os.listdir(root) if
             os.path.isfile(root + '/' + i) and os.path.splitext(i)[1] in trans_list]

    [trans_file(file, encoding) for file in files]


def traversalDir_FirstDir(path):
    mlist = []
    if (os.path.exists(path)):
        # 获取该目录下的所有文件或文件夹目录路径
        files = glob.glob(path + '\\*')
        # print(files)
        for file in files:
            # 判断该路径下是否是文件夹
            if (os.path.isdir(file)):
                mlist.extend(traversalDir_FirstDir(file))
            else:
                (filepath, tempfilename) = os.path.split(file)
                mlist.append(tempfilename)
    return mlist


def createView(templetesPath, viewPath, encoding="utf8", request_name='req'):
    with open(viewPath, "w+", encoding=encoding) as f:
        f.write('from django.shortcuts import render, render_to_response\n')
        f.write("from django.views.decorators.http import require_GET, require_POST\n")
        f.write('import json\n\n\n')
        mlist = traversalDir_FirstDir(templetesPath)
        for each in mlist:
            (shotname, extension) = os.path.splitext(each)
            f.write("@require_GET\n")
            f.write("def " + shotname + "("+request_name+"):\n")
            f.write("    return render_to_response('" + each + "')\n\n")


def add_view_to_urls(templatesPath, urlPath, appName, newUrlPath=None, encoding='utf8'):
    if not newUrlPath:
        newUrlPath = urlPath
    splitext = os.path.splitext(urlPath)
    name_list = traversalDir_FirstDir(templatesPath)
    flag = False
    with open(urlPath, "r", encoding=encoding) as fin, open("{}.bak".format(splitext[0]), "w",
                                                            encoding=encoding) as fout:
        lines = fin.readlines()
        for line in lines:
            if line.find("from django.contrib import admin") >= 0:
                fout.write("from django.conf.urls import url\n")
                fout.write("from {}.views import *\n".format(appName))
            elif line.find("path('admin/', admin.site.urls),") >= 0 or line.find(
                    'path("admin/", admin.site.urls),') >= 0:
                flag = True
            fout.write(line)
            if flag:
                for each in name_list:
                    v = os.path.splitext(each)[0]
                    fout.write("    url(r'^{}$', {})".format(v, v) + ",\n")
                flag = False
    if os.path.exists(newUrlPath):
        os.remove(newUrlPath)
    os.rename("{}.bak".format(splitext[0]), newUrlPath)


if __name__ == '__main__':
    add_view_to_urls("E:\\cxl\\codes\\python\\snowland-Homepage\\homepage\\templates",
                     "E:\\cxl\\codes\\python\\snowland-Homepage\\snowland_homepage\\urls.py",
                     "homepage")
