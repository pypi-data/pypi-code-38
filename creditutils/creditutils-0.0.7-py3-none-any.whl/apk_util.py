# -*- coding:UTF-8 -*-

'''
Created on 2013-8-15

@author: caifenghua
'''

import creditutils.exec_cmd as exec_cmd
import re
import creditutils.trivial_util as util
import creditutils.system_util as system_util
import traceback
import subprocess
import zipfile
import os.path

SIGNED_SUFFIX = '_signed'


def _get_apk_item_info(src_string, dst_dict):
    item_re = re.compile('(\w+)=\'([^\']*)\'')
    infos = item_re.findall(src_string)
    #     print(infos)
    if infos:
        for item in infos:
            dst_dict[item[0]] = item[1]

    return dst_dict


def get_apk_info(apk_path, aapt_path=None):
    if not aapt_path:
        aapt_path = 'aapt'

    cmd_format = '"{0}" d badging "{1}"'
    cmd_str = cmd_format.format(aapt_path, apk_path)
    result = exec_cmd.run_cmd_for_stdout_ignores_exit_code(cmd_str)

    package_re = 'package:\s+([^\r\n]+)'
    application_re = 'application:\s+([^\r\n]+)'

    dict_ = {}
    match = re.search(package_re, result, flags=re.IGNORECASE)
    if not match:
        raise Exception('run cmd failed!')
    else:
        data_str = match.group(1)
        # print(data_str)
        _get_apk_item_info(data_str, dict_)

    match = re.search(application_re, result, flags=re.IGNORECASE)
    if not match:
        raise Exception('run cmd failed!')
    else:
        data_str = match.group(1)
        #         print(data_str)
        _get_apk_item_info(data_str, dict_)

    return dict_


def unzip(zip_file, dst_dir):
    with zipfile.ZipFile(zip_file) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dst_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)


def unzip_specified_file(zip_file, src_file, dst_dir):
    with zipfile.ZipFile(zip_file) as zf:
        if src_file in zf.namelist():
            #             print('to extract the file')
            zf.extract(src_file, dst_dir)
        else:
            #             print('not exist the file')
            msg_format = 'not exist the file {0}'
            msg_info = msg_format.format(src_file)
            raise ValueError(msg_info)


def get_apk_package_name(zip_file, aapt_path=None):
    apk_items = get_apk_info(zip_file, aapt_path=aapt_path)

    package_flag = 'name'
    return apk_items[package_flag]


def unzip_apk_icon(zip_file, dst_dir, aapt_path=None):
    path_split = '\\'
    apk_items = get_apk_info(zip_file, aapt_path=aapt_path)

    package_flag = 'name'
    icon_flag = 'icon'

    dst_dir = dst_dir + path_split + apk_items[package_flag]
    unzip_specified_file(zip_file, apk_items[icon_flag], dst_dir)
    items = re.split('[\\\/]', apk_items[icon_flag])
    relative_path = path_split.join(items)

    return dst_dir + path_split + relative_path


def unzip_apk_dex(zip_file, dst_dir, dex_name='classes.dex'):
    path_split = '\\'

    unzip_specified_file(zip_file, dex_name, dst_dir)
    items = re.split('[\\\/]', dex_name)
    relative_path = path_split.join(items)

    return dst_dir + path_split + relative_path


def decompile_apk(zip_file, dst_dir, apktool_path=None):
    if not apktool_path:
        cmd_format = 'apktool.bat d -f -o {} {}'
        cmd_str = cmd_format.format(dst_dir, zip_file)

    else:
        cmd_format = '{} d -f -o {} {}'
        cmd_str = cmd_format.format(apktool_path, dst_dir, zip_file)

    os.system(cmd_str)

    return dst_dir


class Extractor(object):
    _EXTRACT_CMD_FORMAT = '"{0}" d badging "{1}"'

    _PACKAGE_RE = 'package:\s+([^\r\n]+)'
    _APPLICATION_RE = 'application:\s+([^\r\n]+)'

    NAME_FLAG = 'name'
    _LABEL_FLAG = 'label'

    PATH_SPLIT = '\\'

    PACKAGE_FLAG = 'package'
    VER_CODE_FLAG = 'versionCode'
    VER_NAME_FLAG = 'versionName'
    ICON_FLAG = 'icon'
    SIZE_FLAG = 'size'

    def __init__(self, exe_path=None, apk_info_path=None, log=None):
        self.exe_path = exe_path
        self.aapt_path = self.exe_path + '\\aapt'
        self.apk_info_path = apk_info_path
        self.log = lambda info: log(info) if log else None

    def _get_apk_info(self, apk_path):
        cmd_str = Extractor._EXTRACT_CMD_FORMAT.format(self.aapt_path, apk_path)
        result = exec_cmd.run_cmd_for_stdout_ignores_exit_code(cmd_str.encode(system_util.get_sytem_encoding()))

        dict_ = {}
        match = re.search(Extractor._PACKAGE_RE, result, flags=re.IGNORECASE)
        if not match:
            info_format = 'Run {0} failed!'
            info = info_format.format(cmd_str)
            raise Exception(info)
        else:
            data_str = match.group(1)
            _get_apk_item_info(data_str, dict_)

        match = re.search(Extractor._APPLICATION_RE, result, flags=re.IGNORECASE)
        if not match:
            info_format = 'Run {0} failed!'
            info = info_format.format(cmd_str)
            raise Exception(info)
        else:
            data_str = match.group(1)
            _get_apk_item_info(data_str, dict_)

        return dict_

    def _get_full_path(self, package, relative_path):
        path_split = Extractor.PATH_SPLIT

        full_path = self.apk_info_path + path_split + package

        items = re.split('[\\\/]', relative_path)
        relative_path = path_split.join(items)
        full_path = full_path + path_split + relative_path

        return full_path

    @staticmethod
    def _unzip_apk_file(zip_file, relative_path, dst_dir):
        unzip_specified_file(zip_file, relative_path, dst_dir)

    @staticmethod
    def _convert_str(str_):
        return util.decode_to_unicode(str_) if str_ != '' else str_

    def extract_apk_info(self, apk_path):
        info = {}

        try:
            apk_info = self._get_apk_info(apk_path)
            apk_name = self._convert_str(apk_info[Extractor._LABEL_FLAG])
            apk_package = self._convert_str(apk_info[Extractor.NAME_FLAG])
            apk_ver_code = self._convert_str(apk_info[Extractor.VER_CODE_FLAG])
            apk_ver_name = self._convert_str(apk_info[Extractor.VER_NAME_FLAG])

            icon_relative_path = apk_info[Extractor.ICON_FLAG]
            apk_icon_path = self._get_full_path(apk_package, icon_relative_path)
            dst_dir = self.apk_info_path + Extractor.PATH_SPLIT + apk_package
            self._unzip_apk_file(apk_path, icon_relative_path, dst_dir)
            size = os.path.getsize(apk_path)

            info[Extractor.NAME_FLAG] = apk_name
            info[Extractor.PACKAGE_FLAG] = apk_package
            info[Extractor.VER_CODE_FLAG] = apk_ver_code
            info[Extractor.VER_NAME_FLAG] = apk_ver_name
            info[Extractor.ICON_FLAG] = apk_icon_path
            info[Extractor.SIZE_FLAG] = size
        except Exception:
            except_str = traceback.format_exc()
            self.log(str(except_str))

        return info


class ApkSigner:
    # _SIGN_FORMAT = 'jarsigner -digestalg SHA1 -sigalg MD5withRSA -keystore {} -storepass {} -signedjar {} {} {}'

    # apksign.bat 内容如下，具体路径请依据本机环境进行配置
    # @echo off
    # set JAR_PATH=%ANDROID_HOME%\build-tools\28.0.3\lib\apksigner.jar
    # java -jar %JAR_PATH% sign %*
    _SIGN_FORMAT = 'apksign.bat --ks {} --ks-pass pass:{} --ks-key-alias {}  --key-pass pass:{} --out {} {}'

    def __init__(self, keystore, storepass, storealias, aliaspass=None):
        self.keystore = keystore
        self.storepass = storepass
        self.storealias = storealias
        if not aliaspass:
            self.aliaspass = storepass
        else:
            self.aliaspass = aliaspass

    def sign(self, src_file, dst_file):
        src_file = os.path.abspath(src_file)
        dst_file = os.path.abspath(dst_file)
        if os.path.exists(dst_file):
            os.remove(dst_file)

        sign_cmd = ApkSigner._SIGN_FORMAT.format(self.keystore, self.storepass, self.storealias, self.aliaspass, dst_file, src_file)
        rtn = subprocess.run(sign_cmd, shell=True, check=True, universal_newlines=True)
        return rtn.returncode == 0


def get_default_signed_path(src_path):
    first_part, ext_part = os.path.splitext(src_path)
    return first_part + SIGNED_SUFFIX + ext_part


def sign_apk(keystore, storepass, storealias, src_file, dst_file=None, aliaspass=None):
    signer = ApkSigner(keystore, storepass, storealias, aliaspass)
    if not dst_file:
        dst_file = get_default_signed_path(src_file)

    return signer.sign(src_file, dst_file)


def zipalign(src_file, dst_file):
    # zipalign.bat内容如下，具体路径请依据本机环境进行配置
    # @echo off
    # set BIN_PATH=%ANDROID_HOME%\build-tools\28.0.3\zipalign.exe
    # %BIN_PATH% %*
    # _ALIGN_FORMAT = 'zipalign.bat -v -f 4 {} {}'
    _ALIGN_FORMAT = 'zipalign.bat -f 4 {} {}'
    src_file = os.path.abspath(src_file)
    dst_file = os.path.abspath(dst_file)

    if not os.path.isfile(src_file):
        raise Exception(f'{src_file} not exists!')

    if src_file == dst_file:
        raise Exception(f'{src_file} and {dst_file} is the same file!')

    if os.path.isfile(dst_file):
        os.remove(dst_file)

    to_run_cmd = _ALIGN_FORMAT.format(src_file, dst_file)
    subprocess.run(to_run_cmd, shell=True, check=True, universal_newlines=True)


def zipalign_check(src_file):
    # zipalign.bat内容如下，具体路径请依据本机环境进行配置
    # @echo off
    # set BIN_PATH=%ANDROID_HOME%\build-tools\28.0.3\zipalign.exe
    # %BIN_PATH% %*
    # _ALIGN_FORMAT = 'zipalign.bat -c -v 4 {}'
    _ALIGN_FORMAT = 'zipalign.bat -c 4 {}'
    src_file = os.path.abspath(src_file)

    to_run_cmd = _ALIGN_FORMAT.format(src_file)
    rtn = subprocess.run(to_run_cmd, shell=True, check=False, universal_newlines=True)
    return rtn.returncode == 0
