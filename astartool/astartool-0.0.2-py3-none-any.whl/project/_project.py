#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _project.py
# @time: 2019/6/8 11:53
# @Software: PyCharm


__author__ = 'A.Star'

import datetime
import os
import re
import sys
import warnings
from collections import OrderedDict

from astartool.common import list_allow_extension, list_ignore, item_field, item_foreignkey
from astartool.setuptool import get_version

# from astartool.string import _


type_disp_mapper = {
    'IntegerField': '整型',
    'DateTimeField': '时间类型',
    'CharField': '变长字符串',
    'EmailField': '邮箱类型'
}

field_disp_mapper = OrderedDict({
    'type': '类型',
    'verbose_name': '名称',
    'max_length': '最大长度',
    'model': '模型',
    'auto_created': '是否自动生成',
    'auto_now': '是否自动更新',
    'on_delete': '删除',
    'blank': '可否为空格',
    'null': '可否为空',
    'unique': '是否唯一'
})


def check_exist(to_file):
    if os.path.exists(to_file):
        warnings.warn('file ' + to_file + ' exist')
        txt = input('remove file?\n[Y]yes\n[N]no\n')
        if txt[0] is 'Y' or txt[0] is 'y':
            os.remove(to_file)
        else:
            sys.exit()


def file_to_lines(src_file,
                  to_file='out.txt',
                  start_file='\n',
                  end_file='\n'):
    """
    文件打印到字符串中
    :param src_file: 源文件
    :param to_file: 目标文件
    :param start_file: 文件头
    :param end_file: 文件尾
    :return:
    """
    with open(to_file, 'a+', encoding='utf-8') as outfile, open(src_file, 'rb') as infile:
        lines = infile.readlines()
        try:
            lines = [each_line.decode('gbk') for each_line in lines]
        except BaseException as e:
            # print(e)
            try:
                lines = [each_line.decode('utf8') for each_line in lines]
            except BaseException as e:
                # print(e)
                print("encode exception")
                return
                # lines = [each_line.decode('unicode') for each_line in lines]
        outfile.write(src_file)
        outfile.write('\n')
        outfile.write(start_file)
        outfile.writelines(lines)
        outfile.write(end_file)


def walk(root,
         to_file='out.txt',
         start_file='\n',
         end_file='\n',
         allow_extension=list_allow_extension,
         ignore=list_ignore):
    for i in os.listdir(root):
        flag = True
        for each in ignore:
            if '*' in each:
                try:
                    if re.findall(each, i):
                        flag = False
                        break
                except:
                    pass
            else:
                if i == each or (i == each[:-1] and each.endswith('/')):
                    flag = False
                    break
        if flag:
            src_file = os.path.join(root, i)
            if os.path.isfile(src_file):
                if os.path.splitext(src_file)[1] in allow_extension and src_file not in ignore:
                    file_to_lines(src_file=src_file,
                                  to_file=to_file,
                                  start_file=start_file,
                                  end_file=end_file
                                  )
            else:
                walk(src_file, to_file, start_file, end_file, allow_extension, ignore)


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension,
                     ignore=list_ignore):
    """
    项目打印为文件（申请软著用）
    :param src_project: 源文件项目根目录
    :param to_file: 转化到的文件名
    :param start_file: 文件开始
    :param end_file: 文件结束
    :param allow_extension: 需要转换的文件后缀
    :param ignore: 忽略转换的文件和文件夹
    :return:
    """
    check_exist(to_file)
    walk(src_project, to_file, start_file, end_file, allow_extension, ignore)


def model_to_dict(model_path, encoding='utf-8'):
    """
    数据库模型文件导出成dict（基于文件处理）
    :param model_path:
    :param encoding:
    :return:
    """
    ## 读取模型文件
    with open(model_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
    class_name = ''
    dictionary = OrderedDict({})  # 待返回的结果
    item = OrderedDict({})  # 待处理的字典
    ## 分行处理
    for line in lines:
        if line.startswith('#'):
            # 过滤掉注释
            pass
        elif line.startswith('class'):
            # 处理类名
            name = line.split(' ')[1].split('(')[0]
            class_name = name
            dictionary[name] = {}
            item = {}
        elif line.startswith('  ') or line.startswith('\t'):
            # 处理字段名
            col = line.split('=', 1)
            if len(col) >= 2:
                name = col[0].strip()
                item[name] = {}
                value = col[1].strip().split('(')
                type_name = value[0]
                fields_string = value[1].split(')')[0]
                fields_item = fields_string.split(',')
                item[name]['type'] = type_name.split('.')[-1]
                if item[name]['type'] != 'ForeignKey':
                    for i, each in enumerate(fields_item):
                        c = each.split('=')
                        if len(c) == 2:
                            item[name][c[0].strip()] = c[1].strip()
                        else:
                            item[name][item_field[i]] = c[0].strip()
                else:
                    # 处理字段属性
                    for i, each in enumerate(fields_item):
                        each = each.strip()
                        if each == '':
                            continue
                        c = each.split('=')
                        if len(c) == 2:
                            item[name][c[0].strip()] = c[1].strip()
                        else:
                            item[name][item_foreignkey[i]] = c[0].strip()
            else:
                pass
        else:
            if class_name == '':
                continue
            dictionary[class_name] = dict(dictionary[class_name], **item)
            item = OrderedDict({})
    if item is not None and item is not {}:
        dictionary[class_name] = dict(dictionary[class_name], **item)
    return dictionary


def model_to_doc(model_path, to_file=None,
                 version: (tuple, str) = (0, 0, 1, 'final', 0),
                 datetime=datetime.datetime.now(),
                 title='自动生成数据库模板头',
                 auth='ASTARTOOL ROBOT',
                 *, encoding='utf-8'):
    if isinstance(version, tuple):
        version = get_version(version)
    if to_file is None:
        to_file = 'database_model(auto v{}).md'.format(version)
    check_exist(to_file)
    model_dict = model_to_dict(model_path, encoding=encoding)
    with open(to_file, 'w', encoding=encoding) as f:
        ## 文件头
        f.write("# " + title + '\n\n')
        f.write("**Version: {}**\n".format(version))
        f.write("**Auth:    {}**\n".format(auth))
        f.write("**Date:    {}**\n".format(datetime))

        f.write('\n\n')

        for no, (each_class_key, each_class_values) in enumerate(model_dict.items()):
            f.write(str(no) + '. ' + each_class_key + '\n\n')
            f.write('|字段|字段描述|字段类型|字段信息|\n')
            f.write('|:--:|:--:|:--:|:--:|\n')
            for item_key, item_values in each_class_values.items():
                verbose_name = item_values.pop('verbose_name', item_key)
                item_type = item_values.pop('type', verbose_name)
                item_info = [field_disp_mapper.get(k, k) + ':' + str(v) for k, v in item_values.items()]
                f.write('|'.join(
                    [item_key, verbose_name, type_disp_mapper.get(item_type, item_type), ','.join(item_info)]) + '\n')
            f.write('\n')

