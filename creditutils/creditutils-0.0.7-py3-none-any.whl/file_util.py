# -*- coding:UTF-8 -*-

import os
import sys
import codecs
from argparse import ArgumentError
import re
import chardet.universaldetector as det_
import shutil
import types

unix_sep = '/'


# def get_path():
#     path_getcwd = os.getcwd()
#     path_realpath = os.path.split(os.path.realpath(__file__))[0]
#     path_abspath = os.path.split(os.path.abspath(sys.argv[0]))[0]
#     path_syspath = sys.path[0]
#     print("path_getcwd is: %s" %path_getcwd)
#     print("path_realpath is: %s " %path_realpath)
#     print("path_abspath is: %s " %path_abspath)
#     print("path_sys is: %s" %path_syspath)


def get_real_dir(file_name):
    return os.path.split(os.path.realpath(file_name))[0]


# 将路径归一化，避免路径分隔符不一致引起问题
def normalpath(file_path, sep=None):
    if not sep:
        sep = os.sep
    return sep.join(re.split('[\\\/]+', file_path))


# 将路径归一化，避免路径分隔符不一致引起问题
def normal_unix_path(file_path):
    return normalpath(file_path, sep=unix_sep)


def join_unix_path(*args):
    return unix_sep.join(args)

def import_code(code, name, add_to_sys_modules=False):
    # code can be any object containing code: a string, a file object, or
    # a compiled code object.  Returns a new module object initialized
    # by dynamically importing the given code, and optionally adds it
    # to sys.modules under the given name.
    #
    module = types.ModuleType(name)
    if add_to_sys_modules:
        sys.modules[name] = module

    exec(code, module.__dict__)  # @UndefinedVariable

    return module


def detect_file_enc(file_name):
    utf_8_bom_size = 3
    utf_8_bom_flag = b'\xef\xbb\xbf'

    enc_name = None
    file = open(file_name, 'rb')
    data = file.read(utf_8_bom_size)
    file.close()
    if data == utf_8_bom_flag:
        enc_name = 'utf-8-sig'

    usock = open(file_name, 'rb')
    detector = det_.UniversalDetector()
    for line in usock.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    usock.close()

    #     print(detector.result)

    if enc_name:
        detector.result['encoding'] = enc_name

    return detector.result


def read_file_content(file_name, encoding_=None):
    if not encoding_:
        enc_result = detect_file_enc(file_name)
        encoding_ = enc_result['encoding']
    #     print('encoding: ' + encoding_)
    fh = codecs.open(file_name, encoding=encoding_)
    # Read ALL
    data = fh.read()
    fh.close()

    return data


def read_file_lines(file_name, encoding_=None):
    if not encoding_:
        enc_result = detect_file_enc(file_name)
        encoding_ = enc_result['encoding']
    fh = codecs.open(file_name, encoding=encoding_)
    # Read ALL
    lines = fh.readlines()
    fh.close()

    return lines


def read_file_first_line(file_name, encoding_=None):
    if not encoding_:
        enc_result = detect_file_enc(file_name)
        encoding_ = enc_result['encoding']
    fh = codecs.open(file_name, encoding=encoding_)
    # Read ALL
    line = fh.readline()
    fh.close()

    return line


def read_valid_string_list_from_file(file_name):
    valid_list = []

    if file_name:
        lines = read_file_lines(file_name)
        for line in lines:
            if not re.compile('^\s*$').match(line):
                valid_line = line.strip()
                valid_list.append(valid_line)

    return valid_list


def write_to_file(name, data, encoding=None):
    fh = codecs.open(name, 'w', encoding=encoding)
    fh.write(data)
    fh.close()


def get_dict_from_file(name):
    if name:
        lines = read_file_lines(name)
        dict_result = dict()
        for line in lines:
            array = line.split(',')
            # print(array[0], array[1], array[2])
            if array and len(array) >= 2:
                dict_result[array[0].strip()] = array[1].strip()

        return dict_result
    else:
        str_info = 'file name is invalid'
        raise ArgumentError(str_info)


# 替换文件中的指定字符串
def replace_string_in_file(file_name, src_dst_list):
    enc_result = detect_file_enc(file_name)
    encoding = enc_result['encoding']
    fh = codecs.open(file_name, 'r', encoding=encoding)
    # Read ALL
    ori = fh.read()
    fh.close()

    newer = ori
    for (src_str, dst_str) in src_dst_list:
        newer = newer.replace(src_str, dst_str)

    if newer != ori:
        write_to_file(file_name, newer, encoding)


def process_dir(src_dir, func, *args, **dicts):
    for root, dirs, files in os.walk(src_dir):
        for name in files:
            file_path = os.path.join(root, name)
            func(file_path, *args, **dicts)


def process_dir_src_to_dst(src_dir, dst_dir, func, *args, **dicts):
    if not src_dir.endswith(os.sep):
        src_dir += os.sep

    if not dst_dir.endswith(os.sep):
        dst_dir += os.sep

    for root, _, files in os.walk(src_dir):
        for name in files:
            file_path = os.path.join(root, name)
            dst_path = file_path.replace(src_dir, dst_dir)

            # 不再做可能冗余的创建文件父目录操作
            # base_dst_dir = os.path.dirname(dst_path)
            # if not os.path.exists(base_dst_dir):
            #     os.makedirs(base_dst_dir)

            func(file_path, dst_path, *args, **dicts)


def get_name_without_suffix(file_name):
    match = re.match('(.*)\.\w+$', file_name, re.I)
    if match:
        return match.group(1)
    else:
        return file_name


def replace_file(src, dst):
    if os.path.isfile(dst):
        os.remove(dst)

    base_dst_dir = os.path.dirname(dst)
    if not os.path.exists(base_dst_dir):
        os.makedirs(base_dst_dir)

    shutil.copyfile(src, dst)


def get_child_dirs(parent_dir='.'):
    root_dir = os.path.abspath(parent_dir)
    sub_list = os.listdir(root_dir)
    sub_dir_list = []
    for item in sub_list:
        item_path = root_dir + os.sep + item
        if os.path.isdir(item_path):
            sub_dir_list.append(item_path)

    return sub_dir_list


def get_child_files(parent_dir='.'):
    root_dir = os.path.abspath(parent_dir)
    sub_list = os.listdir(root_dir)
    sub_file_list = []
    for item in sub_list:
        item_path = root_dir + os.sep + item
        if os.path.isfile(item_path):
            sub_file_list.append(item_path)

    return sub_file_list


class FileListRecord:
    def __init__(self):
        self.files = []

    # 调用一次，记录一次文件列表
    def __call__(self, file_path):
        if file_path not in self.files:
            self.files.append(file_path)

    def get_relative_list(self, root_path=None, sep=os.sep):
        if root_path:
            result = []
            if root_path.endswith(os.sep):
                start_path = root_path
            else:
                start_path = root_path + os.sep

            for item in self.files:
                if item.startswith(start_path):
                    result.append(sep.join(re.split('[\\\/]+', item[len(start_path):])))

            result.sort()

            return result
        else:
            result = self.files[:]
            result.sort()

            return result


def get_file_list(src_dir, sep=os.sep):
    rec = FileListRecord()
    src_dir = os.path.abspath(src_dir)
    process_dir(src_dir, rec)
    return rec.get_relative_list(src_dir, sep=sep)


def get_middle_name(src_name, suffix=None):
    if not suffix:
        suffix = '_middle4temp'

    filename, extension = os.path.splitext(src_name)
    return filename + suffix + extension


def get_middle_path(src_path, suffix=None):
    file_path, filename = os.path.split(src_path)
    return os.path.join(file_path, get_middle_name(filename, suffix))


if __name__ == '__main__':
    # file_name = r'D:\temp\for_test.txt'
    # result = detect_file_enc(file_name)
    # print(result)
    # print(result['encoding'])
    # fh = codecs.open(file_name, encoding=result['encoding'])
    # print(fh.read())
    # fh.close()
    pass

