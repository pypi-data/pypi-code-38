import importlib
import sys
import os
from os import listdir
from os.path import isfile, join
import path_helpers as Ph
from logging_decorator import logging

@logging
def __get_files_from_path():
    filter_paths = Ph.get_paths_for_plugin('filters')
    all_filter_files = []
    for filter_path in filter_paths:
        if filter_path not in sys.path:
            sys.path.insert(0, filter_path)
        all_filter_files.extend( [join(filter_path, f) for f in listdir(filter_path) if isfile(join(filter_path, f))] )
    return all_filter_files

@logging
def __get_files_as_list(filter_files):
    files_list = []
    for filter_file in filter_files:
        if filter_file[-3:].lower() == ".py" and filter_file.lower() != "__init__.py":
            files_list.append(filter_file)
    return list(set(files_list))

@logging
def __get_filters_file_list():
    filter_files = __get_files_from_path()
    return __get_files_as_list(filter_files)

@logging
def __get_filters_list():
    filters_list = []
    for filter_file in FILTERED_BUFFERS_FILE_LIST:
        filters_list.append(os.path.splitext(os.path.basename(filter_file))[0])
    return list(set(filters_list))

FILTERED_BUFFERS_FILE_LIST = __get_filters_file_list()
FILTERED_BUFFERS_LIST = __get_filters_list()

@logging
def filter_lines_for_buffer(lines, buffer_name):
    if buffer_name.lower() in FILTERED_BUFFERS_LIST:
        lines = filter_string(lines, buffer_name)
    return lines

@logging
def filter_string(lines, filter_name):
    if filter_name.lower() in FILTERED_BUFFERS_LIST:
        buffer_filter = __get_buffer_filter(filter_name)
        return buffer_filter(lines).processed_lines
    return lines

@logging
def __get_buffer_filter(filter_name):
    importlib.import_module(filter_name)
    return getattr(sys.modules[filter_name], filter_name)
