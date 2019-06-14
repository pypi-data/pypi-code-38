# -*- coding:UTF-8 -*-

'''
Created on 2014年4月29日

@author: work_cfh
'''

import os
import creditutils.exec_cmd as exec_cmd
import shutil
import creditutils.file_util as myfile
import re
import time
import subprocess

DEBUG_FLAG = "debug"
RELEASE_FLAG = "release"

DEBUG_MODE = 1
RELEASE_MODE = 2

MODE_MAP = {DEBUG_MODE: DEBUG_FLAG, RELEASE_MODE: RELEASE_FLAG}
FLAG_MODE_MAP = {DEBUG_FLAG: DEBUG_MODE, RELEASE_FLAG: RELEASE_MODE}

_BUILD_SUCCESS_RE = 'BUILD\s+SUCCESSFUL'


# example: "[echo] Debug Package: D:\version_build\pytxxy\code\20150723_1\pytxxy\bin\pytxxy-debug.apk"

def _get_apk_path_re(mode):
    return '\[echo\]\s+' + mode + '\s+Package\:\s*([^\s]+)\s*$'


# 到指定目录执行命令生成指定版本apk
def make_apk(work_path, mode=RELEASE_MODE):
    make_apk_with_gradle(work_path, mode)


# 到指定目录执行gradle命令生成指定版本apk
def make_apk_with_gradle(work_path, mode=RELEASE_MODE):
    dir_change = False
    pre_cwd = os.getcwd()
    if os.path.abspath(pre_cwd) != os.path.abspath(work_path):
        os.chdir(os.path.dirname(work_path))
        dir_change = True

    try:
        clean_cmd = os.path.dirname(work_path) + os.sep + 'gradlew --configure-on-demand clean'
        print(clean_cmd)
        #         args = []
        #         args.append(clean_cmd.split())
        #
        #         subprocess.check_call(args)
        os.system(clean_cmd)

        # 当前暂时不能区分debug和release版本，后续再调整
        build_cmd = os.path.dirname(work_path) + os.sep + 'gradlew --configure-on-demand assemble{}'.format(
            MODE_MAP[mode].capitalize())
        print(build_cmd)
        #         args = []
        #         args.append(build_cmd.split())
        #         subprocess.check_call(args)
        os.system(build_cmd)
    except subprocess.CalledProcessError:
        raise
    finally:
        if dir_change:
            os.chdir(pre_cwd)


# 到指定目录执行ant命令生成指定版本apk
def make_apk_with_ant(work_path, mode=RELEASE_MODE):
    dir_change = False
    pre_cwd = os.getcwd()
    if os.path.abspath(pre_cwd) != os.path.abspath(work_path):
        os.chdir(work_path)
        dir_change = True

    apk_path = None

    try:
        clean_cmd = 'ant clean'
        exec_cmd.run_cmd_and_check_output_in_specified_dir(work_path, clean_cmd, _BUILD_SUCCESS_RE)
        apk_path_re = _get_apk_path_re(MODE_MAP[mode])
        build_cmd = 'ant ' + MODE_MAP[mode]
        apk_path = run_cmd_and_get_apk_result(build_cmd, _BUILD_SUCCESS_RE, apk_path_re, print_flag=True)

    except Exception as e:
        print(e)
        return False, apk_path
    finally:
        if dir_change:
            os.chdir(pre_cwd)

    return True, apk_path


def replace_file(src, dst):
    if os.path.exists(dst) and os.path.isfile(dst):
        os.remove(dst)

    base_dst_dir = os.path.dirname(dst)
    if not os.path.exists(base_dst_dir):
        os.makedirs(base_dst_dir)

    shutil.copyfile(src, dst)


def run_cmd_and_get_apk_result(dst_dir, cmd_str, result_re, apk_path_re, print_flag=False):
    result = exec_cmd.run_cmd_for_output_in_specified_dir(dst_dir, cmd_str, print_flag)
    match = re.search(result_re, result, flags=re.IGNORECASE)
    if not match:
        raise Exception('run cmd failed!')

    match = re.search(apk_path_re, result, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        raise Exception('run cmd failed!')
    else:
        apk_path = match.group(1)

    return apk_path


class ReplaceError(Exception):
    pass


class ArgumentError(Exception):
    pass


class VersionConfigUpdater:
    VER_CODE_PATTERN = '^(\s*android\s*\:\s*versionCode\s*=\s*")(\d+)(")'
    VER_NAME_PATTERN = '^(\s*android\s*\:\s*versionName\s*=\s*")([\d\.]+)(")'

    def __init__(self, config_path, inner_version=False):
        self.config_path = config_path
        self.config_data = myfile.read_file_content(self.config_path)
        self.config_modified = False

        ver_code_ptn = re.compile(VersionConfigUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))
        ver_code_match = ver_code_ptn.search(self.config_data)
        if ver_code_match:
            self.version_code = ver_code_match.group(2)
        else:
            self.version_code = ''

        ver_name_ptn = re.compile(VersionConfigUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))
        ver_name_match = ver_name_ptn.search(self.config_data)
        if ver_name_match:
            self.version_name = ver_name_match.group(2)
        else:
            self.version_name = ''

        self.inner_version = inner_version

    def _update_version_code(self):
        ptn = re.compile(VersionConfigUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))

        modify_flag = False
        new_str = None
        match = ptn.search(self.config_data)
        if match:
            modify_flag = True
            ori_ver_code = match.group(2)
            new_ver_code = '{}'.format(int(ori_ver_code) + 1)
            self.version_code = new_ver_code
            new_str = match.group(1) + new_ver_code + match.group(3)

        if modify_flag:
            self.config_modified = True
            self.config_data = ptn.sub(new_str, self.config_data)

    def _update_version_name(self):
        ptn = re.compile(VersionConfigUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))

        modify_flag = False
        new_str = None
        match = ptn.search(self.config_data)
        if match:
            modify_flag = True
            ori_ver_name = match.group(2)
            name_list = None
            if ori_ver_name:
                name_list = ori_ver_name.split('.')
                index_a = 2
                if len(name_list) < index_a:
                    name_list.append('0')

                index_b = 3
                if len(name_list) < index_b:
                    name_list.append('1')
                else:
                    build_code = None
                    new_build_value = int(name_list[index_b - 1]) + 1
                    build_code = str(new_build_value)

                    name_list[index_b - 1] = build_code

                index_c = 4
                if len(name_list) < index_c:
                    if self.inner_version:
                        name_list.append(time.strftime('%Y%m%d'))
                else:
                    if not self.inner_version:
                        name_list = name_list[:index_c - 1]

            if name_list:
                new_ver_name = '.'.join(name_list)
            else:
                new_ver_name = ori_ver_name

            self.version_name = new_ver_name
            new_str = match.group(1) + new_ver_name + match.group(3)

        if modify_flag:
            self.config_modified = True
            self.config_data = ptn.sub(new_str, self.config_data)

    def update_version_config(self):
        self._update_version_code()
        self._update_version_name()

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')


class ManifestVerInfoUpdater:
    VER_CODE_PATTERN = '^(\s*android\s*\:\s*versionCode\s*=\s*")(\d+)(")'
    VER_NAME_PATTERN = '^(\s*android\s*\:\s*versionName\s*=\s*")([^"]+)(")'

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = myfile.read_file_content(self.config_path)
        self.config_modified = False

        ver_code_ptn = re.compile(ManifestVerInfoUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))
        ver_code_match = ver_code_ptn.search(self.config_data)
        if ver_code_match:
            self.version_code = ver_code_match.group(2)
        else:
            self.version_code = ''

        ver_name_ptn = re.compile(ManifestVerInfoUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))
        ver_name_match = ver_name_ptn.search(self.config_data)
        if ver_name_match:
            self.version_name = ver_name_match.group(2)
        else:
            self.version_name = ''

    def _update_version_code(self, version_code=None):
        if version_code:
            if version_code != self.version_code:
                ptn = re.compile(ManifestVerInfoUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))

                modify_flag = False
                new_str = None
                match = ptn.search(self.config_data)
                if match:
                    modify_flag = True
                    self.version_code = version_code
                    new_str = match.group(1) + version_code + match.group(3)
                else:
                    raise Exception("Not found the versionCode flag!")

                if modify_flag:
                    self.config_modified = True
                    self.config_data = ptn.sub(new_str, self.config_data)

    def _update_version_name(self, version_name=None):
        if version_name:
            if version_name != self.version_name:
                ptn = re.compile(ManifestVerInfoUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))

                modify_flag = False
                new_str = None
                match = ptn.search(self.config_data)
                if match:
                    modify_flag = True
                    self.version_name = version_name
                    new_str = match.group(1) + version_name + match.group(3)
                else:
                    raise Exception("Not found the versionName flag!")

                if modify_flag:
                    self.config_modified = True
                    self.config_data = ptn.sub(new_str, self.config_data)

    def update_version_config(self, version_code=None, version_name=None):
        self._update_version_code(version_code)
        self._update_version_name(version_name)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')


class GradleVerInfoUpdater:
    VER_CODE_PATTERN = '^(\s*versionCode\s*=?\s*)(\d+)(\s*)$'
    VER_NAME_PATTERN = '^(\s*versionName\s*=?\s*")([^"]+)("\s*)$'

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = myfile.read_file_content(self.config_path)
        self.config_modified = False

        ver_code_ptn = re.compile(GradleVerInfoUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))
        ver_code_match = ver_code_ptn.search(self.config_data)
        if ver_code_match:
            self.version_code = ver_code_match.group(2)
        else:
            self.version_code = ''

        ver_name_ptn = re.compile(GradleVerInfoUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))
        ver_name_match = ver_name_ptn.search(self.config_data)
        if ver_name_match:
            self.version_name = ver_name_match.group(2)
        else:
            self.version_name = ''

    def _update_version_code(self, version_code=None):
        if version_code:
            if version_code != self.version_code:
                ptn = re.compile(GradleVerInfoUpdater.VER_CODE_PATTERN, flags=(re.I | re.M))

                modify_flag = False
                new_str = None
                match = ptn.search(self.config_data)
                if match:
                    modify_flag = True
                    self.version_code = version_code
                    new_str = match.group(1) + version_code + match.group(3)
                else:
                    raise Exception("Not found the versionCode flag!")

                if modify_flag:
                    self.config_modified = True
                    self.config_data = ptn.sub(new_str, self.config_data)
                    print('update version code with {}.'.format(self.version_code))
                else:
                    print('version code remain as {}.'.format(self.version_code))

    def _update_version_name(self, version_name=None):
        if version_name:
            if version_name != self.version_name:
                ptn = re.compile(GradleVerInfoUpdater.VER_NAME_PATTERN, flags=(re.I | re.M))

                modify_flag = False
                new_str = None
                match = ptn.search(self.config_data)
                if match:
                    modify_flag = True
                    self.version_name = version_name
                    new_str = match.group(1) + version_name + match.group(3)
                else:
                    raise Exception("Not found the versionName flag!")

                if modify_flag:
                    self.config_modified = True
                    self.config_data = ptn.sub(new_str, self.config_data)
                    print('update version name with {}.'.format(self.version_name))
                else:
                    print('version name remain as {}.'.format(self.version_name))

    def update_version_config(self, version_code=None, version_name=None):
        self._update_version_code(version_code)
        self._update_version_name(version_name)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')


class ManifestConfigInfoUpdater:
    # meta-data example: <meta-data android:name="JPUSH_CHANNEL" android:value="developer-default"/>
    _META_DATA_PATTERN_FORMAT = '(\s*<\s*meta\-data\s+android\s*\:\s*name\s*=\s*"{}"\s+android\s*\:\s*value\s*=\s*")([^"]*)("\s*/>)'

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = myfile.read_file_content(self.config_path)
        self.config_modified = False

    def get_single_meta_data(self, name):
        if name:
            ptn_str = ManifestConfigInfoUpdater._META_DATA_PATTERN_FORMAT.format(re.escape(name))
            ptn = re.compile(ptn_str, flags=(re.I | re.M))

            match = ptn.search(self.config_data)
            value = None
            if match:
                value = match.group(2)

            return value

    def _update_single_meta_data(self, name, value):
        if name:
            ptn_str = ManifestConfigInfoUpdater._META_DATA_PATTERN_FORMAT.format(re.escape(name))
            ptn = re.compile(ptn_str, flags=(re.I | re.M))

            modify_flag = False
            match = ptn.search(self.config_data)
            if match:
                ori_value = match.group(2)
                if value and ori_value != value:
                    modify_flag = True
                    new_str = match.group(1) + value + match.group(3)
            else:
                raise Exception("Not found the meta-data with name of {}!".format(name))

            if modify_flag:
                self.config_modified = True
                self.config_data = ptn.sub(new_str, self.config_data)

    def update_single_meta_data(self, name, value):
        self._update_single_meta_data(name, value)
        if self.config_modified:
            info = 'update meta_data {} with "{}".'.format(name, value)
        else:
            info = 'meta_data {} remain as "{}".'.format(name, value)
        print(info)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')

    def update_multi_meta_data(self, meta_data_map):
        if meta_data_map:
            for key in meta_data_map:
                self._update_single_meta_data(key, meta_data_map[key])
                info = 'update meta_data {} with "{}".'.format(key, meta_data_map[key])
                print(info)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')


class StringItemUpdater:
    # string item example: <string name="ok">确认</string>
    _ITEM_PATTERN_FORMAT = '(\s*<\s*string\s+name\s*=\s*"{}"\s*>)([^<>]*)(<\s*/\s*string\s*>)'

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = myfile.read_file_content(self.config_path)
        self.config_modified = False

    def get_single_item_value(self, name):
        if name:
            ptn_str = StringItemUpdater._ITEM_PATTERN_FORMAT.format(re.escape(name))
            ptn = re.compile(ptn_str, flags=(re.I | re.M))

            match = ptn.search(self.config_data)
            value = None
            if match:
                value = match.group(2)

            return value

    def _update_single_item_value(self, name, value):
        if name:
            ptn_str = StringItemUpdater._ITEM_PATTERN_FORMAT.format(re.escape(name))
            ptn = re.compile(ptn_str, flags=(re.I | re.M))

            modify_flag = False
            match = ptn.search(self.config_data)
            if match:
                ori_value = match.group(2)
                if value and ori_value != value:
                    modify_flag = True
                    new_str = match.group(1) + value + match.group(3)
            else:
                raise Exception("Not found the string item with name of {}!".format(name))

            if modify_flag:
                self.config_modified = True
                self.config_data = ptn.sub(new_str, self.config_data)

    def update_single_item(self, name, value):
        self._update_single_item_value(name, value)
        if self.config_modified:
            info = 'update string item {} with "{}".'.format(name, value)
        else:
            info = 'string item {} remain as "{}".'.format(name, value)
        print(info)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')

    def update_multi_item(self, item_map):
        if item_map:
            for key in item_map:
                self._update_single_item_value(key, item_map[key])
                info = 'update string item {} with "{}".'.format(key, item_map[key])
                print(info)

        if self.config_modified:
            myfile.write_to_file(self.config_path, self.config_data, 'utf-8')


if __name__ == '__main__':
    pass
