
import os, shutil, sys, errno, ntpath
import subprocess # for executing shell commands 
import urllib.request
from urllib import error
import tarfile
import time
import datetime

# ---------------------------------------------------------------------------------------------------------------------
# Files and directories


def file_exists(path_to_file):
    """
    True if file exists, false otherwise (or if it is a directory).
    """
    if os.path.isdir(path_to_file):
        return False
    return os.path.exists(path_to_file)


def dir_exists(path_to_dir):
    """
    True if directory exists, false otherwise (or if it is a file).
    """
    return os.path.isdir(path_to_dir)


def symlink_exists(path):
    return os.path.islink(path)


def path_base_and_leaf(path):
    """
    Splits path to a base part and a file or directory name, as in the following example:
    path: '/a/b'; base: '/a'; leaf: 'b'
    """
    head, tail = ntpath.split(path)
    if not tail:  # in case there is trailing slash at the end of path
        return {'base': ntpath.split(head)[0], 'leaf': ntpath.basename(head)}
    return {'base': head, 'leaf': tail}


def silent_write_text_file(filename, contents=''):
    """
    Create a new text file and writes contents into it (do not raise exceptions).
    If file with specified name already exists, it will be overwritten.
    :return: Dict - 'error': empty string if success, or error message otherwise.
    """
    result = {'error': ''}
    try:
        f = open(filename, 'w')
        f.write(contents)
        f.close()
        return result
    except Exception as e:
        result['error'] = str(e)
        return result


def silent_read_text_file(filename):
    """
    Read a text file (do not raise exceptions).
    :param filename: path to file
    :return: Dict - 'error': empty string if success, or error message otherwise;
                    'contents': file contents if success;
    """
    result = {'contents': '', 'error': ''}
    if not file_exists(filename):
        result['error'] = 'file_not_exists'
        return result
    try:
        file = open(filename, 'r')
        result['contents'] = file.read()
        file.close()
    except Exception as e:
        result['contents'] = ''
        result['error'] = str(e)
    return result


def silent_create_path(path, overwrite=False):
    """
    Create a path on a filesystem (do not raise exceptions).
    :param path: path to be created
    :param overwrite: if true, existing old directory will be overwritten
    :return: Dict - 'error': empty string if success, or error message otherwise;
    """
    result = {'error': ''}
    try:
        if dir_exists(path):
            if not overwrite:
                return result
            remove_dir(path)
        os.makedirs(path)
    except Exception as e:
        result['error'] = str(e)
        return result
    return result


def remove_file(path):
    os.remove(path)


def silent_remove_file(filename):
    """
    Remove the file from the file system (do not raise exceptions).
    :param filename:
    :return: Dict - 'error': empty string if the file was removed or not exists,
                            or error message otherwise;
    """
    result = {'error': ''}
    if file_exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            result['error'] = str(e)
    return result


def silent_remove_symlink(path):  # TODO: test
    """
    Remove symlink from the file system (do not raise exceptions).
    :param path: string
    :return: Dict - 'error': empty string if the link was removed or not exists,
                    or error message otherwise;
    """
    result = {'error': ''}
    if symlink_exists(path):
        try:
            os.unlink(path)
        except OSError as e:
            result['error'] = str(e)
    return result


def remove_dir(dirname):
    shutil.rmtree(dirname)


def silent_remove_dir(path):
    """
    Remove directory and all its contents (a tree) from the file system (do not raise exceptions).
    :param path:
    :return: Dict - 'error': empty string if the directory was removed or not exists, or error message otherwise;
    """
    result = {'error': ''}
    if dir_exists(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            result['error'] = str(e)
    return result


def silent_copy_file(origin, dest):
    """
    Copy a file (do not raise exception).
    :param origin:
    :param dest:
    :return: Dict - 'error': empty string if existing file was copied, or error message otherwise;
    """
    result = {'error': ''}
    if not file_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if silent_remove_file(dest)['error']:
        result['error'] = "old file can't be removed"
        return result
    try:
        shutil.copy(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def silent_move_file(origin, dest):
    """
    Move a file (do not raise exception).
    :param origin:
    :param dest:
    :return: Dict - 'error': empty string if existing file was moved, or error message otherwise;
    """
    result = {'error': ''}
    if not file_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if silent_remove_file(dest)['error']:
        result['error'] = "old file can't be removed"
        return result
    try:
        shutil.move(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def silent_copy_dir(origin, dest):
    """
    Copy a directory and its contents (a tree) to a dest (do not raise exception).
    If old 'dest' exists, it will be removed first.
    :param origin:
    :param dest:
    :return: Dict - 'error': empty string if directory was copied and exists or error message otherwise;
    """
    result = {'error': ''}
    if not dir_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if silent_remove_dir(dest)['error']:
        result['error'] = "old directory can't be removed"
        return result
    try:
        shutil.copytree(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def silent_move_dir(origin, dest):
    """
    Move a directory and its contents (a tree) into a dest (do not raise exception).
    If old 'dest' exists, it will be removed first.
    This function is equivalent to 'rename'.
    :param origin:
    :param dest:
    :return: Dict - 'error': empty string if success or error message otherwise;
    """
    result = {'error': ''}
    if not dir_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if silent_remove_dir(dest)['error']:
        result['error'] = "old directory can't be removed"
        return result
    try:
        shutil.move(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def get_subdirs(path):
    """
    List of all first child subdirectories that the directory contains.
    :param path:
    :return: Dict - 'subdirs': list of subdirectory names
                    'error': empty string if success or error message otherwise;
    """
    result = {'subdirs': [], 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    result['subdirs'] = [subdir.name for subdir in os.scandir(path) if subdir.is_dir()]
    return result


def get_file_list(path):
    """
    List of files located in the directory.
    :param path:
    :return: Dict - 'files': list of files located in the directory;
                    'error': empty string if success or error message otherwise;
    """
    result = {'files': [], 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    result['files'] = [file.name for file in os.scandir(path) if file.is_file()]
    return result


def get_dir_item_count(path):
    """
    Total number of child elements in the directory.
    :param path:
    :return: Dict - 'count': number of child items in the directory;
                    'error': empty string if success or error message otherwise;
    """
    result = {'count': 0, 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    result['count'] = len([item.name for item in os.scandir(path)])
    return result


def dir_empty(path):
    """
    Check if directory is empty.
    :param path:
    :return: True or False
    """
    return not get_dir_item_count(path)['count']


def get_filesystem_item_type(item_name):
    """
    Type of the file system item.
    Supported type names: 'file', 'dir, 'symlink'
    :param item_name:
    :return: Dict - 'type': string that describes the type; empty string is returned if type is unknown or item
                            does not exist;
                    'exists': boolean - True if item exists or false otherwise.
    """
    result = {'exists': False, 'type': ''}
    if file_exists(item_name):
        result['exists'] = True
        result['type'] = 'file'
    elif dir_exists(item_name):
        result['exists'] = True
        result['type'] = 'dir'
    elif symlink_exists(item_name):
        result['exists'] = True
        result['type'] = 'symlink'
    return result


# ---------------------------------------------------------------------------------------------------------------------
# Operations with strings


def substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0, to_index=-1,
                           include_trailing_newline=False):
    """
    Get first substring between initial and terminal key sequence if present in data,
    e.g. if data is '[[my_val]]', initial_seq is '[[', and terminal_seq is ']]',
    the result is {'value': 'my_val', 'start': 0, 'end': 8, 'error': ''};
    :param data: string
    :param initial_seq: string
    :param terminal_seq: string
    :param from_index: index from which to start search
    :param to_index: index where to stop search (not including it), -1 means the data end
    :param include_trailing_newline: if true, result['end'] will be advanced to include trailing new line chars;
    :return: Dict:  'value' (everything between initial and terminal sequence,
                    'start', 'end' (open range, index of next character after teminal_seq end)
                    'error': empty string if no errors, 'syntax' otherwise
    """
    result = {'value': '', 'start': -1, 'end': -1, 'error': ''}
    if to_index == -1:
        start = data.find(initial_seq, from_index)
    else:
        start = data.find(initial_seq, from_index, to_index)
    if start == -1:
        return result
    result['start'] = start
    if to_index == -1:
        end = data.find(terminal_seq, start)
    else:
        end = data.find(terminal_seq, start, to_index)
    if end == -1:
        result['error'] = 'syntax'
        return result
    result_end = end + len(terminal_seq)

    if include_trailing_newline:
        # Search for trailing '\n' and/or '\r' symbols and
        # include them into the range
        data_len = len(data)
        if data_len - result_end >= 2:
            if data[result_end] == '\r' or data[result_end] == '\n':
                result_end += 1
            if data[result_end] == '\r' or data[result_end] == '\n':
                if data[result_end] != data[result_end - 1]:
                    result_end += 1
        elif data_len - result_end == 1:
            if data[result_end] == '\r' or data[result_end] == '\n':
                result_end += 1
    result['end'] = result_end
    result['value'] = data[start + len(initial_seq):end]
    return result


def extract_substr_enclosed_in_seq(the_string, initial_seq, terminal_seq, from_index=0, to_index=-1,
                                   include_trailing_newline=False):
    """
    Extracts first substring enclosed in matching initial and terminal keys from data,
    e.g. if data is '[[my_val]]_remainder', initial_seq is '[[', and terminal_seq is ']]',
    the result is {'extracted': 'my_val', 'remainder': '_remainder', 'error': ''};
    :param the_string: string
    :param initial_seq: string
    :param terminal_seq: string
    :param from_index: index from which to start search
    :param to_index: index where to stop search (not including it), -1 means the data end
    :param include_trailing_newline: if true, result['end'] will be advanced to include trailing new line chars;
    :return: Dict:  'extracted' (everything between initial and terminal sequence),
                    'remainder' - data with removed 'extracted' part,
                    'error': empty string if no errors, 'syntax' otherwise
    """
    result = {'extracted': '', 'remainder': the_string, 'error': ''}
    found = substr_enclosed_in_seq(the_string, initial_seq, terminal_seq,
                                   from_index, to_index, include_trailing_newline)
    if found['error']:
        result['error'] = found['error']
        return result
    result['extracted'] = found['value']
    result['remainder'] = the_string[0:found['start']]
    result['remainder'] += the_string[found['end']:]
    return result


def strip_quotes(data):
    """
    Strips whitespaces and then quotes (single or double) at both sides of data.
    :param data: string
    :return: dict: 'value': everything inside single or double quotes,
                   'error': empty string if no errors or 'syntax' if quote at the beginning has no matching
                   quote at the end
    """
    result = {'value': '', 'error': 'syntax'}
    data = data.strip()
    if data == '':
        return result
    # Check if single or double quotes are used
    use_double_quotes = False
    data_len = len(data)
    if data_len == 0:
        return result
    if data[0] != "'" and data[0] != '"':
        # no quotes detected, return original data
        result['value'] = data
        result['error'] = ''
        return result
    if data[0] == '"':
        use_double_quotes = True
    if use_double_quotes:
        if data[data_len - 1] != '"':
            return result
    else:
        if data[data_len - 1] != "'":
            return result
    result['value'] = data[1:data_len - 1]
    result['error'] = ''
    return result


def parse_assignment(line):
    """
    Searches for the first '=' symbol in the line and
    splits it: everything before '=' becomes 'name',
    everything after becomes 'value'.
    E.g.
    my_var = My Value or my_var = 'My Value' or my_var = "My Value"
    :param line: string
    :return: dict: 'name': string that represents variable name,
                   'value': everything between single or double quotes,
                   'error': empty string if no errors or 'syntax' if assign symbol not found
    """
    result = {'name': '', 'value': '', 'error': 'syntax'}
    line.strip()
    if line == '':
        return result
    assign_mark_pos = line.find('=')
    if assign_mark_pos == -1:
        return result
    name = line[0:assign_mark_pos].strip()
    result['name'] = name
    line = line[assign_mark_pos + 1:].strip()
    if not len(line):
        result['value'] = ''
        result['error'] = ''
        return result
    if line[0] != '"' and line[0] != "'":  # Value without quotes
        result['value'] = line
        result['error'] = ''
        return result
    stripped = strip_quotes(line)
    result['value'] = stripped['value']
    result['error'] = stripped['error']
    return result


def strip_whitespaces_in_list(str_list):
    tmp = []
    for line in str_list:
        tmp.append(line.strip())
    return tmp


def remove_empty_lines_from_list(str_list):
    tmp = []
    for line in str_list:
        if len(line):
            tmp.append(line)
    return tmp


def remove_closed_range_from_list(the_list, from_index, to_index):
    """ Removes closed range from 'the_list',
    elements with indexes 'from_index' and 'to_index' are also removed."""
    doc_len = len(the_list)
    if from_index < 0:
        from_index = 0
    if to_index < from_index:
        to_index = from_index
    if from_index > doc_len - 1:
        return the_list
    if to_index > doc_len - 1:
        to_index = doc_len - 1
    tmp = []
    for i in range(0, from_index):
        tmp.append(the_list[i])
    for i in range(to_index + 1, doc_len):
        tmp.append(the_list[i])
    return tmp


def open_range_sublist(the_list, from_index, to_index):
    """
    Returns an open range sublist of 'the_list', 'to_index' is not included.
    :param the_list:
    :param from_index:
    :param to_index:
    :return: sublist of 'the_list' or empty list if indexes are out of range
    """
    tmp = []
    list_len = len(the_list)
    if from_index < 0:
        from_index = 0
    if to_index < 0 or to_index > list_len:
        to_index = list_len
    if to_index < from_index:
        to_index = from_index
    if from_index > list_len - 1:
        return tmp
    for i in range(from_index, to_index):
        tmp.append(the_list[i])
    return tmp


def split_line_into_cmd_and_args(line):
    """
    Splits a string into list of strings, where first element represents command and the rest are arguments.
    Arguments may be in single or double quotes, quotes are stripped from the result.
    :param line: string that looks like a shell command, e.g. "run 'first task' -b"
    :return: Dict, e.g. {'cmd': 'run', 'args': ['first task', '-b'], 'error': ''}
    """
    result = {'cmd': '', 'args': [], 'error': 'syntax'}
    line = line.strip()
    extracted = extract_first_word(line)
    if extracted['error']:
        return result
    result['cmd'] = extracted['value']
    line = extracted['remainder']
    while True:
        line = line.strip()
        if not len(line):
            result['error'] = ''
            return result
        if line[0] == "'":
            extracted = extract_first_value_in_quotes(line, "'")
        elif line[0] == '"':
            extracted = extract_first_value_in_quotes(line, '"')
        else:
            extracted = extract_first_word(line)

        if extracted['error']:
            return result
        result['args'].append(extracted['value'])
        line = extracted['remainder']


def extract_first_word(line):
    """
    Extracts first word from a string where words are separated with whitespaces.
    Line is left-stripped from whitespaces before extraction.
    :param line: string
    :return: Dict: 'value' - extracted first word if any;
                    'remainder' - the remainder after extractions;
                    'error' - empty string if success or error message if any;
    """
    line = line.lstrip()
    result = {'value': '', 'remainder': line, 'error': ''}
    if not len(line):
        return result
    whitespace_pos = line.find(' ')
    if whitespace_pos == -1:
        result['value'] = line
        result['remainder'] = ''
        return result
    result['value'] = line[0:whitespace_pos]
    remainder_start_index = min(whitespace_pos+1, len(line))
    result['remainder'] = line[remainder_start_index:]
    return result


def extract_first_value_in_quotes(line, quote_mark):
    """
    Extracts first value in quotes (single or double) from a string.
    Line is left-stripped from whitespaces before extraction.
    :param line: string
    :param quote_mark: type of quotation mark: ' or "
    :return: Dict: 'value': extracted value;
                    'remainder': the remainder after extraction
                    'error' empty string if success or 'syntax' otherwise;
    """
    line = line.lstrip()
    result = {'value': '', 'remainder': line, 'error': 'syntax'}
    if len(line) < 2:
        return result
    if line[0] != quote_mark:
        return result
    next_qm_pos = line.find(quote_mark, 1)
    if next_qm_pos == -1:
        return result
    result['value'] = line[1:next_qm_pos]
    result['remainder'] = line[next_qm_pos + 1:]
    result['error'] = ''
    return result


def remove_selected_from_list(the_list, selected_indexes):
    """
    Removes selected elements from the list.
    :param the_list:
    :param selected_indexes: list of indexes to be removed from the list
    :return: processed list
    """
    doc_len = len(the_list)
    tmp = []
    for i in range(0, doc_len):
        if i not in selected_indexes:
            tmp.append(the_list[i])
    return tmp


def find_line_starting_with_seq(the_list, seq, from_index=0, to_index=-1):
    """
    Returns index of line in the document that starts with specified char sequence. Or -1 if sequence not found.
    :param the_list: list of strings
    :param seq: char sequence to find;
    :param from_index: index in the list;
    :param to_index: index in the list, open range; if is negative, the list will be searched till the end;
    :return: index of the first occurrence of 'seq' in the list or -1 if not found
    """
    if to_index < 0:
        to_index = len(the_list)
    if from_index > to_index:
        from_index = to_index
    for i in range(from_index, to_index):
        if the_list[i].startswith(seq):
            return i
    return -1


def replace_keys(the_string, the_dict):
    """
    Replace all keys with their values in 'the_string'
    :param the_string:
    :param the_dict:
    :return: processed string
    """
    for key, value in the_dict.items():
        the_string = the_string.replace(key, value)
    return the_string


def replace_in_string_list(the_list, the_dict):
    """
    Replace all keys with their values in each string of 'the_list'.
    :param the_list: a list of strings
    :param the_dict: replacement dictionary
    :return: processed list
    """
    tmp = []
    for line in the_list:
        for key, val in the_dict.items():
            line = line.replace(key, val)
        tmp.append(line)
    return tmp


# ---------------------------------------------------------------------------------------------------------------------
# Environment variables

def setEnvVar(variableName, value):
    os.environ[variableName] = value

def getEnvVar(variableName):
    if not variableName in os.environ:
        return ''
    return os.environ[variableName]

def unsetEnvVar(variableName):
    if variableName in os.environ:
        del os.environ[variableName]

def envVarExists(variableName):
    return variableName in os.environ


# ---------------------------------------------------------------------------------------------------------------------
# Execute shell commands

# 'cmdAndArgs' must be an array, each argument must be a separate array element
def executeShellCmd(cmdAndArgs):
    subprocess.check_call(cmdAndArgs, env=dict(os.environ))


# ---------------------------------------------------------------------------------------------------------------------
# Zip, tar, gzip archives

def unzipTarGz(archFile, destDir, removeArchFile=False):
    if not file_exists(archFile):
        return
    if not dir_exists(destDir):
        silent_create_path(destDir)
    with tarfile.open(archFile, 'r:*') as t:
            t.extractall(destDir)
            t.close()
    if removeArchFile:
        silent_remove_file(archFile)


def zipFileTarGz(sourceFile, destArchName, removeSourceFile=False):
    if not file_exists(sourceFile):
        return
    with tarfile.open(destArchName, "w:gz") as tar:
        tar.add(sourceFile, arcname=os.path.basename(sourceFile))
    if removeSourceFile:
        remove_file(sourceFile)


def zipDirTarGz(sourceDir, destArchName, removeSourceDir=False):
    if not dir_exists(sourceDir):
        return
    with tarfile.open(destArchName, "w:gz") as tar:
        tar.add(sourceDir, arcname=os.path.basename(sourceDir))
    if removeSourceDir:
        silent_remove_dir(sourceDir)


# ---------------------------------------------------------------------------------------------------------------------
# File download

def silentDownloadFile(fileUrl, destFileName):
    result = ['']
    try:
        result = urllib.request.urlretrieve(fileUrl, destFileName)
    except error.URLError as e:
        pass 
    return result


# ---------------------------------------------------------------------------------------------------------------------
# Git operations (simplified)


def gitClone(gitUrl, path):
    if dir_exists(path):
        silent_remove_dir(path)
    cmd = ['git', 'clone', gitUrl, path]
    executeShellCmd(cmd)


def gitPull(path):
    if not dir_exists(path):
        return
    oldPath = os.getcwd()
    os.chdir(path)
    cmd = ['git', 'pull']
    executeShellCmd(cmd)
    os.chdir(oldPath)


# ---------------------------------------------------------------------------------------------------------------------
# Timers
# class OneShotTimer:
#     def __init__(self, timeout, callback):
#         self._timeout = timeout
#         self._callback = callback
#         self._task = asyncio.ensure_future(self._job())
#
#     async def _job(self):
#         await asyncio.sleep(self._timeout)
#         await self._callback()
#
#     def cancel(self):
#         self._task.cancel()


# ---------------------------------------------------------------------------------------------------------------------
# Date and time

def utc_timestamp_millis():
    return int(round(time.time() * 1000))


def current_year_utc():
    """
    Current year in time zone UTC+00::00 as a string
    :return: string
    """
    return str(datetime.datetime.now(datetime.timezone.utc).year)


def current_date_utc():
    """
    Current date in time zone UTC+00::00 as a string
    :return: string
    """
    return str(datetime.datetime.now(datetime.timezone.utc).date())


def current_datetime_utc():
    """
    Current date and time in time zone UTC+00::00 as a string
    :return: string
    """
    return str(datetime.datetime.now(datetime.timezone.utc))


def current_time_utc():
    """
    Current time in time zone UTC+00::00 as a string
    :return: string
    """
    return str(datetime.datetime.now(datetime.timezone.utc).time())[0:8] + ' UTC+00:00'

# ---------------------------------------------------------------------------------------------------------------------
# Project-exclusive


def readVersionFile(path):
    return silent_read_text_file(path + '/version.txt')


def writeVersionFile(path, content):
    silent_write_text_file(path + '/version.txt', content)


def removeVersionFile(path):
    silent_remove_file(path + '/version.txt')

