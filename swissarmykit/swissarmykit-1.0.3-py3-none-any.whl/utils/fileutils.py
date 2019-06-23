# -*- coding: utf-8 -*-

import re
import os
import pickle
import csv
import shutil
import string
import zipfile
from pathlib import Path
from shutil import copyfile

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py

class FileUtils():

    @staticmethod
    def get_all_files(path, file_name_only=False):
        if file_name_only:
            return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        path = path[:-1] if path.endswith('/') else path
        return [path + '/' + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    @staticmethod
    def copy_recursive_overwrite(src, dest, ignore=None):
        ''' https://stackoverflow.com/questions/12683834/how-to-copy-directory-recursively-in-python-and-overwrite-all '''
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            if ignore is not None:
                ignored = ignore(src, files)
            else:
                ignored = set()
            for f in files:
                if f not in ignored:
                    FileUtils.copy_recursive_overwrite(os.path.join(src, f), os.path.join(dest, f), ignore)
        else:
            shutil.copyfile(src, dest)
            print('INFO: Copy %s -> %s' % (src, dest))

    @staticmethod
    def zipfiles(files: list = None, path='None', file_name='files.zip'):
        if files:
            zipf = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
            for file in files:
                if os.path.exists(file) and os.path.isfile(file):
                    zipf.write(file)
            zipf.close()

    @staticmethod
    def cp_flatten_only_format(root, format='.mobi'):
        dst = FileUtils.mkdir(root + '/flatten_folder')
        files_stage = {}
        for path, subdirs, files in os.walk(root):
            for name in files:
                if name.endswith(format):
                    src = os.path.join(path, name)
                    files_stage[src] = path

        for src, path in files_stage.items():
            shutil.copy(src, dst)  # file -> dir
            print('INFO: cp: %s -> %s' % (src, dst))

    @staticmethod
    def cp(src, dst):
        ''' Note: Be careful with create dir.'''
        try:
            if os.path.isfile(src):
                path = dst.rsplit('/', 1)[0]
                FileUtils.mkdir(path)  # Make folder parent.
                copyfile(src, dst)  # file -> dir
                # shutil.copyfile(src, dst) # file -> file
                # shutil.copy(src, dst)   # file -> dir
                print('INFO: cp: %s -> %s' % (src, dst))
        except Exception as e:
            print('error', e)

    @staticmethod
    def rename_extension(file_path, new_ext):
        pre, ext = os.path.splitext(file_path)
        os.rename(file_path, pre + new_ext)
        print('INFO: rename %s -> %s' % (file_path, (pre + new_ext)))

    @staticmethod
    def cp_all(src_path, dst):
        if not os.path.exists(dst):
            FileUtils.mkdir(dst)

        if os.path.isdir(src_path) and os.path.isdir(dst):
            for file in os.listdir(src_path):
                file_path = src_path + '/' + file
                FileUtils.cp(file_path, dst + '/' + file)
        else:
            raise Exception('ai_: src_path and dst must be directory')

    @staticmethod
    def flatten_all_file(destination, depth=None):
        if not depth:
            depth = []
        path = [destination] + depth
        path = os.path.join(*path)

        for file_or_dir in os.listdir(path):
            file = path + os.sep + file_or_dir
            file_exists = destination + os.sep + file_or_dir
            if os.path.isfile(file):
                if os.path.exists(file_exists):
                    print('Warn: file exist %s at destination' % (file))
                else:
                    shutil.move(file, destination)
                    print('Info: move %s -> %s' % (file, destination))
            else:
                path_2 = depth + [file_or_dir]
                FileUtils.flatten_all_file(destination, [os.path.join(*path_2)])

    @staticmethod
    def delete_empty_folder(destination):
        for file_or_dir in os.listdir(destination):
            dir = destination + os.sep + file_or_dir
            if os.path.isdir(dir) and not os.listdir(dir):
                print('empty folder')

    @staticmethod
    def mkdir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
            return dir
        return dir

    @staticmethod
    def get_file_size(path):
        return os.path.getsize(path)

    @staticmethod
    def cache(key=None, data=None):
        path = appConfig.DIST_PATH + os.sep + key
        FileUtils.to_html_file(path=path, data=data)
        print('INFO: Cache %s' % path)
        return data

    @staticmethod
    def get_cache(key=None, data=None):
        path = appConfig.DIST_PATH + os.sep + key
        if data:
            return FileUtils.cache(key=key, data=data)
        print('INFO: Get cache %s' % path)
        return FileUtils.load_html_file(path=path)

    @staticmethod
    def read_file(path=None):
        if not path:
            path = appConfig.DIST_PATH + os.sep + 'text.txt'
        return FileUtils.load_html_file(path=path)

    @staticmethod
    def write_binary_file(path=None, data=None):
        if not path:
            path = appConfig.DIST_PATH + os.sep + 'text.txt'

        output_file = open(path, 'wb')
        output_file.write(data)
        output_file.close()
        print('Write binary file %s ' % path)

    @staticmethod
    def get_valid_file_path(filename):
        return FileUtils.remove_disallowed_filename_chars(filename)

    @staticmethod
    def remove_disallowed_filename_chars(filename):
        validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in filename if c in validFilenameChars)

    @staticmethod
    def append_file(path=None, data=None):
        if not path:
            path = appConfig.DIST_PATH + os.sep + 'text.txt'

        appConfig.create_if_not_exist(path)
        with open(path, 'a', encoding='utf-8') as file:
            file.write(data)

    @staticmethod
    def write_file(path=None, data=None):
        if not path:
            path = appConfig.DIST_PATH + os.sep + 'text.txt'
        return FileUtils.to_html_file(path=path, data=data)

    @staticmethod
    def to_html_file(path=None, data=None):
        if not path:
            path = appConfig.DIST_PATH + os.sep + 'to_html.html'
        else:
            path, file = path.rsplit('/', 1)
            path = path + '/' + FileUtils.get_valid_file_path(file)

        FileUtils.mkdir(path)
        Path(path).write_text(data, encoding='utf-8')
        print('INFO: Output file', path)

    @staticmethod
    def output_html_to_desktop(data, file_name=None):
        path = appConfig.USER_DESKTOP + '/' + (file_name if file_name else 'test_.html')
        FileUtils.to_html_file(path, data)
        print('INFO: Output html to desktop', path)

    @staticmethod
    def load_html_file(path=None, as_bytes=False):
        try:
            if not path:
                path = appConfig.DIST_PATH + os.sep + 'to_html.html'
            elif '/' not in path:
                print('todo: implement auto detect path here')

            if as_bytes:
                with open(path, 'rb') as f:
                    contents = f.read()
                return str(contents)

            return Path(path).read_text(encoding='utf-8')
        except Exception as e:
            ''' https://stackoverflow.com/questions/42339876/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xff-in-position-0-in '''
            print('ERROR:  ', e, ' ::  will read as bytes, then convert to str')
            with open(path, 'rb') as f:
                contents = f.read()
            return str(contents)

    @staticmethod
    def to_csv_file(data, path):
        with open(path, 'w', encoding="utf-8", newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in data:
                spamwriter.writerow(row)

    # Dumps pickle
    @staticmethod
    def dump_object_to_file(data=None, path=None):
        if not path:
            path = appConfig.DUMPS_PATH + os.sep + 'tmps.pickle'
        FileUtils.mkdir(path)
        pickle.dump(data, open(path, "wb"))
        print('Dump object at %s' % path)

    # Load pickle
    @staticmethod
    def load_object_from_file(path=None):
        if not path:
            path = appConfig.DUMPS_PATH + os.sep + 'tmps.pickle'

        if path and os.path.exists(path):
            value = pickle.load(open(path, "rb"))
        else:
            return None

        print('Load object at %s' % path)
        return value

    # Print object
    @staticmethod
    def print_dumps_file(path=None):
        if path and os.path.exists(path):
            value = pickle.load(open(path, "rb"))
        else:
            path = appConfig.DUMPS_PATH + os.sep + 'tmps.pickle'
            value = pickle.load(open(path, "rb"))
        print(value)

        # Print object

    @staticmethod
    def rename_dot_mp4(dir):
        list = os.listdir(dir)
        for item in list:
            if item == '.DS_Store':
                continue
            dst = dir + item.replace('.mp4', '[DOT]mp4').replace('.', ' ').replace('[DOT]mp4', '.mp4')
            src = dir + item
            os.rename(src, dst)
            print(src)

    @staticmethod
    def rename_file(path, old, new):
        if os.path.exists(path):
            src = path + old
            dst = path + new
            os.rename(src, dst)
            print(dst)

    @staticmethod
    def get_path_of_file(__file__):
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_size_info(start_path='.'):
        total_size = 0
        files = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                files += 1

        return total_size, files

    @staticmethod
    def info_template():
        from swissarmykit.utils.fileutils import FileUtils
        file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')) + os.sep + 'definitions.py'
        content = FileUtils.read_file(file)
        output = appConfig.ROOT_DIR + os.sep + file.rsplit(os.sep, 1)[-1].replace('.py', '_prod.py')
        # FileUtils.write_file(appConfig.ROOT_DIR + os.sep + file.replace('.py', '_prod.py'), content)
        print('ERROR: Must create this file to determine the ROOT_DIR\n%s \n\n%s' % (output, content))

if __name__ == '__main__':
    f = FileUtils()
    print(f.get_all_files('C:/Users/Will/Desktop/deli/school/private'))