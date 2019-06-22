#!/usr/bin/env python
#coding: utf-8
#by yangbin at 2018.11.28
 
import os


PROJECT_DIR = os.getcwd()
GOPHER_DIR = os.path.join(PROJECT_DIR, 'gopher')
APIDOC_DIR = os.path.join(PROJECT_DIR, 'doc/api')
M2C_PATH = os.path.join(PROJECT_DIR, '.m2c')
BUILD_DIST = os.path.join(PROJECT_DIR, 'dist')
GOMOD_PATH = os.path.join(GOPHER_DIR, 'go.mod')
APIMODEL_PATH = os.path.join(PROJECT_DIR, 'apimodel.txt')
OBJMODEL_PATH = os.path.join(PROJECT_DIR, 'objmodel.txt')
M2C_PROJECT_INIT_URL = 'https://dat-pub.oss-cn-hangzhou.aliyuncs.com/m2c/m2c-0.0.3.zip'
M2C_PROJECT_INIT_NAME = os.path.basename(M2C_PROJECT_INIT_URL)
LOG_HOME = '/data/log'

TYPEMAPPING = {
    'str': 'string',
    '[]str': '[]string',
    'string': 'string',
    '[]string': '[]string',
    'int': 'int64',
    'int32': 'int32',
    'int64': 'int64',
    'long': 'int64',
    'float': 'float64',
    'float64': 'float64',
    'float32': 'float32',
    'double': 'float64',
    '[]int': '[]int64',
    'int32': 'int32',
    '[]int32': '[]int32',
    'int64': 'int64',
    '[]int64': '[]int64',
    'long': 'int64',
    '[]long': '[]int64',
    'float': 'float64',
    '[]float': '[]float64',
    'float64': 'float64',
    '[]float64': '[]float64',
    'float32': 'float32',
    '[]float32': '[]float32',
    'double': 'float64',
    '[]double': '[]float64',
    'time': 'time.Time',
    'bool': 'bool',
    '[]bool': '[]bool',
    'any': 'interface{}',
    'dict': 'map[string]interface{}',
    'JsonNode': 'map[string]interface{}',
}

APIDOC_TYPE = {
    'int64': 'Number',
    'int32': 'Number',
    'int': 'Number',
    'float': 'Number',
    'float32': 'Number',
    'float64': 'Number',
    '[]float': 'Number[]',
    '[]float32': 'Number[]',
    '[]float64': 'Number[]',
    '[]int64': 'Number[]',
    '[]int32': 'Number[]',
    '[]int': 'Number[]',
    'str': 'String',
    '[]str': 'String[]',
    'string': 'String',
    '[]string': 'String[]',
    'interface{}': 'Object',
    '[]interface{}': 'Object[]',
    'bool': 'Boolean',
    '[]bool': 'Boolean[]',
    'object': 'Object',
    '[]object': 'Object[]',
    'number': 'Number',
    '[]number': '[]Number',
    'number[]': 'Number[]', # old
    'object[]': 'Object[]', # old
}

AUTH_TYPE = ['userAuth', 'adminAuth', None]
PROTO_TYPE = ['json', 'raw', 'reqRaw', 'respRaw', None]

TAB_WIDTH = 4
API_MAX_DEEP_NUM = 2

MOD = 'gopher'

OBJ_ALLOWED_PREFIX = ["&", "@", "^"]
OBJ_REF_TYPE_MANAGE = "manage"
OBJ_REF_TYPE_REF = "refer"
OBJ_CONTAINER_TYPE_BASIC = "basic"
OBJ_CONTAINER_TYPE_SINGLE = "single"
OBJ_CONTAINER_TYPE_LIST = "list"
OBJ_CONTAINER_TYPE_TREE = "tree" # TODO
OBJ_MAX_DEEP_NUM = 3

class Color:
    _GREEN = "\033[92m"
    _RED = "\033[91m"
    _BOLD = '\033[1m'
    _ENDC = '\033[0m'

    @staticmethod
    def red(txt):
        return "%s%s%s%s" % (Color._BOLD, Color._RED, txt, Color._ENDC)

    @staticmethod
    def green(txt):
        return "%s%s%s%s" % (Color._BOLD, Color._GREEN, txt, Color._ENDC)
