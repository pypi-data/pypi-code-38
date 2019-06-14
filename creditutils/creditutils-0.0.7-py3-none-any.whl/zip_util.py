# -*- coding:UTF-8 -*-

'''
Created on 2014年1月1日

@author: work_cfh
'''

# 使用zipfile做目录压缩，解压缩功能

import os
import os.path
import zipfile
import re
import creditutils.file_util as file_util


def zip_files(file_items, dst_path, src_root=None, to_print=False):
    pre_len = 0
    if src_root:
        src_root = file_util.normalpath(src_root)
        if src_root.endswith(os.sep):
            pre_len = len(src_root)
        else:
            pre_len = len(src_root) + len(os.sep)

    base_dir = os.path.dirname(dst_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    with zipfile.ZipFile(dst_path, "w", zipfile.zlib.DEFLATED) as zf:
        if to_print:
            print('to pack file to {}:'.format(dst_path))
        for item in file_items:
            if pre_len > 0:
                zip_name = item[pre_len:]
            else:
                zip_name = item

            if to_print:
                print(zip_name)

            zf.write(item, zip_name)


def zip_dir(src_dir, dst_path, src_root=None, to_print=False):
    src_dir = file_util.normalpath(src_dir)
    if not os.path.isdir(src_dir):
        raise Exception('{} is not directory!'.format(src_dir))

    file_items = []
    for root, dirs, files in os.walk(src_dir):
        for name in files:
            file_items.append(os.path.join(root, name))

    # 路径相对目录配置
    if src_root:
        item_pre = src_root
    else:
        item_pre = src_dir

    if item_pre.endswith(os.sep):
        pre_len = len(item_pre)
    else:
        pre_len = len(item_pre) + len(os.sep)

    base_dir = os.path.dirname(dst_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    with zipfile.ZipFile(dst_path, "w", zipfile.zlib.DEFLATED) as zf:
        if to_print:
            print('to pack file to {}:'.format(dst_path))
        for item in file_items:
            if pre_len > 0:
                zip_name = item[pre_len:]
            else:
                zip_name = item

            if to_print:
                print(zip_name)

            zf.write(item, zip_name)


def zip_file(src_path, dst_path, to_print=False):
    if not os.path.isfile(src_path):
        raise Exception('{} is not file!'.format(src_path))

    base_dir = os.path.dirname(dst_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    with zipfile.ZipFile(dst_path, "w", zipfile.zlib.DEFLATED) as zf:
        if to_print:
            print('to pack file {} to {}:'.format(src_path, dst_path))

        zip_name = os.path.basename(src_path)
        zf.write(src_path, zip_name)


def zip_item(src_path, dst_path, to_print=False):
    if os.path.isdir(src_path):
        zip_dir(src_path, dst_path, to_print)
    elif os.path.isfile(src_path):
        zip_file(src_path, dst_path, to_print)
    else:
        raise Exception('{} neither directory nor file!'.format(src_path))


def unzip_file(filepath, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    zfobj = zipfile.ZipFile(filepath)

    for name in zfobj.namelist():
        name_ = name.replace('/', os.sep)

        if name_.endswith(os.sep):
            dir_ = os.path.join(dst_dir, name_)
            if not os.path.exists(dir_):
                os.makedirs(dir_)
        else:
            ext_filename = os.path.join(dst_dir, name_)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.makedirs(ext_dir)

            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

    zfobj.close()


def unzip_specified_file(zip_file, src_file, dst_dir):
    with zipfile.ZipFile(zip_file) as zf:
        # 将路径归一化，避免路径分隔符不一致引起问题
        src_file = '/'.join(re.split('[\\\/]+', src_file))
        if src_file in zf.namelist():
            #             print('to extract the file')
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            zf.extract(src_file, dst_dir)

            # 返回最终输出文件的目录
            path_items = []
            path_items.extend(re.split('[\\\/]+', dst_dir))
            path_items.extend(re.split('[\\\/]+', src_file))
            return os.sep.join(path_items)
        else:
            #             print('not exist the file')
            msg_format = 'not exist the file {0}'
            msg_info = msg_format.format(src_file)
            raise ValueError(msg_info)


def append_file(zip_file, dst_ref_path, src_path):
    if os.path.exists(zip_file):
        if os.path.exists(src_path):
            with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zf:
                zf.write(src_path, dst_ref_path)
        else:
            info = 'source file "{}" not exists'.format(src_path)
            print(info)
    else:
        info = 'target packed file "{}" not exists'.format(zip_file)
        print(info)


def append_file_with_data(zip_file, dst_ref_path, src_data):
    if os.path.exists(zip_file):
        if src_data:
            with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(dst_ref_path, src_data)
        else:
            info = 'source data is empty!'
            print(info)
    else:
        info = 'target packed file "{}" not exists'.format(zip_file)
        print(info)


def get_file_list(zip_file):
    if os.path.exists(zip_file):
        with zipfile.ZipFile(zip_file, 'r') as src_zip:
            result = src_zip.namelist()
            result.sort()

            return result
    else:
        raise Exception('source packed file "{}" not exists'.format(zip_file))


def append_file_with_original_file_list_data(zip_file, dst_ref_path):
    if os.path.exists(zip_file):
        data = '\r\n'.join(get_file_list(zip_file))

        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(dst_ref_path, data)
    else:
        info = 'target packed file "{}" not exists'.format(zip_file)
        print(info)
