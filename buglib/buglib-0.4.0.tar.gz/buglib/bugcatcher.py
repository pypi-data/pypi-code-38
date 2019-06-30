# -*- coding: utf-8 -*-
"""异常问题相关处理和收集"""

import os
import gzip
import base64
import traceback
import faulthandler
import sys
import uuid
import json
import time
import hashlib
import queue
import datetime
from threading import Thread, Lock

BUG_CATCHER_VERSION = 0.4
BUG_CATCHER_NAME = 'BugCatcher'


class BugStruct(object):
    """
    Bug信息的结构体
    """

    def __init__(self):
        super(BugStruct, self).__init__()
        self.is_last = ""
        self.post_data = {
            "project_name": "",
            "project_version": "",
            "project_file_mod_time": "",

            "bug_lib_version": BUG_CATCHER_VERSION,

            "bug_type": "",
            "bug_path": "",
            "bug_data": "",
            "bug_md5": "",
            "bug_info": "",

            "system_info": "",

            "local_time": "",

            "is_fixed": None,
            "is_upload": None,

        }

    def pprint(self):
        import pprint
        pprint.pprint(self.post_data)

    def format_data(self):
        time_obj = datetime.datetime.fromtimestamp(self.post_data['local_time'])
        if self.is_last:
            last_str = '【last】'
        else:
            last_str = ''
        text = """{}
{}[{}][{}] {}{} Catched Error from {}. info:{}
    {}""".format("=" * 140,
                 last_str,
                 time_obj.strftime('%Y-%m-%d %H:%M:%S'),
                 self.post_data['project_name'],
                 BUG_CATCHER_NAME,
                 BUG_CATCHER_VERSION,
                 self.post_data['bug_type'],
                 self.post_data['bug_info'],
                 self.post_data['bug_data'].replace('\n', '\n    ')[:-4])

        return text

    def set_project_name(self, name):
        self.post_data["project_name"] = name

    def set_project_version(self, version):
        self.post_data["project_version"] = version

    def set_project_file_mod_time(self, f_time):
        self.post_data["project_file_mod_time"] = f_time

    def set_bug_info(self, info):
        self.post_data['bug_info'] = info

    def set_system_info(self, system_info):
        self.post_data["system_info"] = system_info

    def set_bug_type(self, bug_type):
        self.post_data["bug_type"] = bug_type

    def set_bug_filename(self, filename):
        """
        设置抛出异常的的文件名
        :param filename:
        :return:
        """
        self_path = os.path.dirname(sys.argv[0])
        self.post_data["bug_path"] = filename.replace(self_path, '')

    def set_bug_data(self, data):
        self.post_data["bug_data"] = data
        self.post_data["bug_md5"] = self.bug_md5()
        self.post_data["local_time"] = time.time()

    @classmethod
    def decrypt_text(cls, text):
        t = gzip.decompress(text)
        t = base64.b64decode(t[::-1])
        return t

    @classmethod
    def encrypt_text(cls, text):
        t = base64.b64encode(text)[::-1]
        t = gzip.compress(t)
        return t

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            data = f.read()
            data = cls.decrypt_text(data).decode()
            data = json.loads(data)
            if data:
                bug_obj = cls()
                bug_obj.is_last = filename
                bug_obj.post_data = data
                return bug_obj

    def dump(self, folder):
        filename = os.path.join(folder, self.post_data['bug_md5'] + '.bug')
        if os.path.exists(filename):
            return False

        with open(filename, 'wb') as f:
            data = json.dumps(self.post_data).encode()
            data = self.encrypt_text(data)
            f.write(data)

    def delete(self):
        if self.is_last:
            os.remove(self.is_last)

    def bug_md5(self):
        if self.post_data['bug_md5']:
            return self.post_data['bug_md5']

        m2 = hashlib.md5()
        m2.update(self.post_data["bug_data"].encode())
        md5_value = m2.hexdigest()
        return md5_value


class SubmitThread(Thread):

    def __init__(self):
        super(SubmitThread, self).__init__()

        self.queue = queue.Queue()

        self.sleep_count = 0

        self.pool = []

    def put(self, bug_obj):
        self.queue.put(bug_obj)

    def post_pool(self):

        self.sleep_count = 0
        self.pool = []

    def run(self):
        while 1:
            # 1024 count
            if self.queue.empty():
                time.sleep(1)
                continue

            obj = self.queue.get(block=False, timeout=1)
            print(obj)
            # time.sleep(60*5)


class CatchThread(Thread):

    def __init__(self, project_path):
        super(CatchThread, self).__init__()

        self.setDaemon(True)

        self.queue = queue.Queue()

        self.unkey_lst = []
        self.output_folder = project_path

        self.print_bug = False

    def put(self, bug_obj):
        self.queue.put(bug_obj)

    def callback(self, bug_obj):
        pass

    def run(self):
        print("{} Thread Running...".format(BUG_CATCHER_NAME))
        while 1:
            bug_obj = self.queue.get()
            if self.print_bug:
                sys.stdout.write(bug_obj.format_data())

            bug_md5 = bug_obj.bug_md5()

            if bug_md5 and bug_md5 in self.unkey_lst:
                continue

            self.unkey_lst.append(bug_md5)

            if bug_obj.dump(self.output_folder):
                self.callback(bug_obj)


class BugCatcherManager(object):

    def __init__(self, project_name):
        super(BugCatcherManager, self).__init__()

        self.project_name = project_name
        self.project_file_mod_time = os.path.getmtime(sys.argv[0])
        self.project_version = self.get_project_version()
        self.system_info = {"mac_adders": self.get_mac_addres()}

        self.bug_md5_lst = []

        self.bug_api_url = ''
        self.bug_api_log = False
        self.bug_file_log = False

        self.queue_thread = None
        self.submit_thread = None

        self.project_folder = None
        self.thread_lock = Lock()

        self.setup_path()

    def start(self):
        if self.queue_thread:
            self.queue_thread.start()

        if self.submit_thread:
            self.submit_thread.start()

    def setup_path(self):

        path = os.path.join(os.getenv('ALLUSERSPROFILE'), BUG_CATCHER_NAME)

        if not os.path.exists(path):
            os.mkdir(path)

        project_path = os.path.join(path, self.project_name)
        if not os.path.exists(project_path):
            os.mkdir(project_path)

        self.project_folder = project_path

        self.queue_thread = CatchThread(project_path)

    def set_bug_api_url(self, url):
        self.bug_api_url = url

    def enable_api_log(self):
        self.bug_api_log = True
        self.submit_thread = SubmitThread()
        self.queue_thread.callback = self.submit_thread.put

    def enable_file_log(self):
        self.bug_file_log = True

    def enable_print_log(self):
        self.queue_thread.print_bug = True

    def enable_sys_catch(self):
        sys.excepthook = self.catch_by_sys_hook

    def enable_stderr_catch(self):
        faulthandler.enable()

        class NullDevice():
            def write(sel, text):
                if text.strip():
                    with self.thread_lock:
                        self.catch_by_stderr(text)

        sys.stderr = NullDevice()

    def read_last_dump(self):
        if os.path.exists(self.project_folder):
            for a in os.listdir(self.project_folder):
                if a.endswith('.bug'):
                    bug_obj = BugStruct.load(os.path.join(self.project_folder, a))
                    if bug_obj:
                        self.caught_bug(bug_obj)

    def caught_bug(self, bug_obj):
        self.queue_thread.put(bug_obj)

    def catch_by_stderr(self, text):
        bug_obj = BugStruct()
        bug_obj.set_bug_type('std_err')
        bug_obj.set_project_name(self.project_name)
        bug_obj.set_project_version(self.project_version)
        bug_obj.set_project_file_mod_time(self.project_file_mod_time)
        bug_obj.set_system_info(self.system_info)
        if 'File ' in text:
            bug_filename = text.split('File ')[-1].split(""', ')[0]
            bug_obj.set_bug_filename(bug_filename)

        bug_obj.set_bug_data(text)
        self.caught_bug(bug_obj)

    def catch_by_try_catch(self, info=None):
        """
        从手动try 中捕获
        :return:
        """
        except_obj = sys.exc_info()
        exc_type, exc_value, tb = except_obj
        bug_obj = BugStruct()
        bug_obj.set_bug_type('try_catch')
        bug_obj.set_project_name(self.project_name)
        bug_obj.set_project_version(self.project_version)
        bug_obj.set_project_file_mod_time(self.project_file_mod_time)
        bug_obj.set_system_info(self.system_info)
        bug_obj.set_bug_filename(tb.tb_frame.f_code.co_filename)
        bug_obj.set_bug_data(''.join(traceback.format_exception(exc_type, exc_value, tb)[1:]))
        bug_obj.set_bug_info(info)
        self.caught_bug(bug_obj)

    def catch_by_sys_hook(self, exc_type, exc_value, tb):
        """
        从系统中捕获
        :param exc_type:
        :param exc_value:
        :param tb:
        :return:
        """
        bug_obj = BugStruct()
        bug_obj.set_bug_type('sys_hook')
        bug_obj.set_project_name(self.project_name)
        bug_obj.set_project_version(self.project_version)
        bug_obj.set_project_file_mod_time(self.project_file_mod_time)
        bug_obj.set_system_info(self.system_info)
        bug_obj.set_bug_filename(tb.tb_frame.f_code.co_filename)
        bug_obj.set_bug_data(''.join(traceback.format_exception(exc_type, exc_value, tb)[1:]))
        self.caught_bug(bug_obj)

    def get_mac_addres(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def get_project_version(cls):
        """
        读取主程序版本信息
        :return:
        """
        root_dir = ''
        version_dat = os.path.join(root_dir, 'version.dat')
        if os.path.exists(version_dat):
            with open(version_dat, 'r') as f:
                value = json.load(f)
                return value.get('version', '?'), value.get('mode', '?')

        else:
            return '?', '?'


if __name__ == '__main__':
    a = BugCatcherManager("test")
    a.enable_print_log()
    a.enable_api_log()
    a.enable_sys_catch()
    a.enable_stderr_catch()
    a.read_last_dump()
    a.start()

    import bug_test

    a.queue_thread.join()
