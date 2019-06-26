from divinegift.logger import log_info, log_err, log_warning
from divinegift.config import Settings
#########################################################################
import sys
from datetime import datetime
import re
import os
import math
from collections import defaultdict
import json
import yaml
import inspect

datetime_regex = r'20\d{2}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))(T|\s)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])'


def dict_compare(d1: dict, d2: dict):
    """
    Compare 2 dict
    :param d1: First dict to compare
    :param d2: Second dict
    :return: Dict with results of comparing
    """
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d2_keys - d1_keys
    removed = d1_keys - d2_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])

    result = {'added': list(added), 'removed': list(removed), 'modified': modified, 'same': list(same)}
    return result


def subset_dict(dict1: dict, dict2: dict):
    return len(set(dict1.items()) & set(dict2.items())) == len(min((dict1, dict2), key=len))


def dict_find_keys(list_dict: list, filter: dict, multiple=True):
    result = [x for x in list_dict if subset_dict(filter, x)]
    if multiple:
        pass
    else:
        if len(result) > 0:
            result = result[0]
        else:
            result = {}
    return result


def get_args():
    """
    Get dict of args by pairs (e.g. --log_level 'INFO')
    :return: dict of args
    """
    args = sys.argv
    args_d = {}
    for i, arg in enumerate(args):
        if i == 0:
            args_d['name'] = arg
            continue
        if arg.startswith('-') or arg.startswith('--'):
            if i != len(args) - 1:
                if not args[i + 1].startswith('-') or not args[i + 1].startswith('--'):
                    args_d[arg] = args[i + 1]
                else:
                    args_d[arg] = True
            else:
                args_d[arg] = True
        else:
            continue

    return args_d


def get_log_param(args: dict):
    """
    Get log_level and log_name from args
    :param args: dict of args from get_args()
    :return: log_level and log_name for set_loglevel()
    """
    log_level = None
    log_name = None
    log_dir = None
    for key in args.keys():
        if key in ['--log_level', '-ll']:
            log_level = args.get(key)
        if key in ['--log_name', '-ln']:
            log_name = args.get(key)
        if key in ['--log_dir', '-ld']:
            log_dir = args.get(key)

    if not log_level:
        log_level = 'INFO'
    if not log_name:
        log_name = None
    if not log_dir:
        log_dir = os.path.join(get_base_dir(), 'logs')

    log_params = {'log_level': log_level, 'log_name': log_name, 'log_dir': log_dir}

    return log_params


def get_base_dir():
    try:
        base_dir = os.getcwd()
    except:
        base_dir = ''

    return base_dir


def get_list_files(path: str, filter=None, filter_not_contain: str = None, add_path: bool = False, path2: str = ''):
    """
    Get filelist with path in folder
    :param path: Folder containing files
    :param filter: filter (regexp-like), could be list of str or just str. None by default
    :param add_path: bool, will needed add path to file or not
    :param path2: path which need to add
    :return: return list of files with/without path to it
    """
    path = os.path.normpath(path)
    list_files = []
    if add_path:
        if path2 == '':
            path2 = path
        else:
            path2 = os.path.normpath(path2)
    else:
        path2 = ''

    if filter_not_contain:
        filter = r'^((?!{filter_not_contain}).)*$'.format(filter_not_contain=filter_not_contain)
    if filter:
        if type(filter) == list:
            for f in filter:
                list_files.extend([os.path.join(path2, x) for x in os.listdir(path) if re.search(f, x)])
        if type(filter) == str:
            list_files = [os.path.join(path2, x) for x in os.listdir(path) if re.search(filter, x)]
    else:
        list_files = [os.path.join(path2, x) for x in os.listdir(path)]
    
    list_files = list(set(list_files))

    return list_files


def get_progress(pb_i: int, pb_m: int, pb_p: int=10):
    pb_s = pb_m / (100 / pb_p)
    if pb_i == 0:
        log_info('{:4.0f}% ({:{}.0f} / {})'.format(0.0, pb_i, len(str(pb_m)), pb_m))
        # return pb_i
    if math.floor((pb_i + 1) % pb_s) == 0:
        log_info('{:4.0f}% ({:{}.0f} / {})'.format((pb_i + 1) / pb_s * pb_p, (pb_i + 1), len(str(pb_m)), pb_m))
        return (pb_i + 1) / pb_s * pb_p
    if pb_i == (pb_m - 1):
        log_info('{:4.0f}% ({:{}.0f} / {})'.format(100.0, pb_i + 1, len(str(pb_m)), pb_m))
        return (pb_i + 1) / pb_s * pb_p

    return None


def get_double(d: list, key: str):
    D = defaultdict(list)
    d = [x.get(key) for x in d]
    for i, item in enumerate(d):
        D[item].append(i)
    D = {k: v for k, v in D.items() if len(v) > 1}

    return D


def check_folder_exist(folder_path: str):
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def simple_translit(text: str):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    result = text.translate(tr)
    return result


def varName(var):
    lcls = inspect.stack()[2][0].f_locals
    for name in lcls:
        if id(var) == id(lcls[name]):
            return name
    return None


def create_json(json_data: object, json_fname: str = None, encoding: str = 'utf-8'):
    if not json_fname:
        json_fname = f'{varName(json_data)}.json'
    j = Json(json_fname, encoding)
    j.set_data(json_data)
    j.create()


def parse_json(json_fname: str, encoding: str = 'utf-8', return_: object = None):
    j = Json(json_fname, encoding, return_)
    return j.parse()
    

def create_yaml(yaml_data: object, yaml_fname: str = None, encoding: str = 'utf-8'):
    if not yaml_fname:
        yaml_fname = f'{varName(yaml_data)}.yml'
    y = Yaml(yaml_fname, encoding)
    y.set_data(yaml_data)
    y.create()


def parse_yaml(yaml_fname: str, encoding: str = 'utf-8', return_: object = None):
    y = Yaml(yaml_fname, encoding, return_)
    return y.parse()


class BaseMl:
    def __init__(self, fname, encoding='utf-8', return_=None):
        if fname:
            file_dir, file_name = os.path.split(fname)
        else:
            file_dir, file_name = None, None
        self.fname = file_name
        self.fpath = file_dir
        self.encoding = encoding
        self.return_ = return_
        self.data = None

    def __repr__(self):
        return f'{self.__cls__}({self.fname}, {self.encoding}, {self.return_}) with {self.data}'

    def reinit(self, fname, encoding='utf-8', return_=None):
        if fname:
            file_dir, file_name = os.path.split(fname)
        else:
            file_dir, file_name = None, None
        self.fname = file_name
        self.fpath = file_dir
        self.encoding = encoding
        self.return_ = return_

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data


class Yaml(BaseMl):
    def parse(self):
        try:
            with open(os.path.join(self.fpath, self.fname), 'r', encoding=self.encoding) as yaml_file:
                self.data = yaml.full_load(yaml_file)
        except:
            self.data = self.return_
        return self.data

    def create(self):
        check_folder_exist(self.fpath)
        with open(os.path.join(self.fpath, self.fname), 'w', encoding=self.encoding) as outfile:
            response = yaml.dump(self.data, outfile, default_flow_style=False, indent=4,
                                 allow_unicode=True, sort_keys=False)


class Json(BaseMl):
    def parse(self):
        try:
            with open(os.path.join(self.fpath, self.fname), 'r', encoding=self.encoding) as json_file:
                json_str = json_file.read()
                self.data = json.loads(json_str, object_hook=self.date_hook)
        except:
            self.data = self.return_
        return self.data

    def create(self):
        check_folder_exist(self.fpath)
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
        with open(os.path.join(self.fpath, self.fname), 'w', encoding=self.encoding) as outfile:
            response = json.dump(self.data, outfile, ensure_ascii=False, default=dthandler, indent=4)

    @staticmethod
    def date_hook(json_dict: object):
        """
        Hook which used for translate date string in json file to datetime type
        :param json_dict: dict from json file
        :return: dict from json after translating
        """
        for (key, value) in json_dict.items():
            try:
                json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except:
                pass
        return json_dict


if __name__ == '__main__':
    pass
