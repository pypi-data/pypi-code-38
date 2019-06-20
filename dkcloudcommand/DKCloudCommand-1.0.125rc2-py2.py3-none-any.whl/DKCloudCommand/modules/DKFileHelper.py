import os
import shutil
import json
import codecs
from datetime import datetime
from DKCommon.DKFileEncode import DKFileEncode


class DKFileHelper:

    def __init__(self):
        pass

    @staticmethod
    def get_file_date(file_path):
        if not os.path.exists(file_path):
            return None

        if not os.path.isfile(file_path):
            return None

        return datetime.fromtimestamp(os.path.getmtime(file_path)).date()

    @staticmethod
    def is_file_contents_binary(file_contents):
        try:
            file_contents.encode('utf8')
            return False
        except:
            return True

    @staticmethod
    def create_dir_if_not_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def create_path_if_not_exists(full_path):
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    @staticmethod
    def clear_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory)

    @staticmethod
    def read_file(full_path, encoding=None, b64_encode_binary_files=False):
        if not os.path.isfile(full_path):
            return ''
        if encoding is None:
            encoding = DKFileEncode.infer_encoding(full_path)

        if 'utf-8' == encoding:
            try:
                with codecs.open(full_path, 'r', encoding='utf-8') as f:
                    return f.read().encode('utf-8')
            except Exception as e:
                message = str(e)
                message += '%sFile name: %s' % (os.linesep, full_path)
                raise Exception(message)
        else:
            with open(full_path, 'rb') as the_file:
                file_contents = the_file.read()
                if b64_encode_binary_files:
                    return DKFileEncode.b64encode(file_contents)
                else:
                    return file_contents

    @staticmethod
    def write_file(full_path, contents, encoding=None):
        path, file_name = os.path.split(full_path)
        DKFileHelper.create_path_if_not_exists(path)
        if isinstance(contents, dict):
            contents = json.dumps(contents)
        with open(full_path, 'wb+') as the_file:
            the_file.seek(0)
            the_file.truncate()
            if encoding == 'base64' and contents is not None:
                the_file.write(DKFileEncode.b64decode(contents))
            elif contents is not None:
                if isinstance(contents, unicode):
                    contents = contents.encode("utf-8")
                the_file.write(contents)


