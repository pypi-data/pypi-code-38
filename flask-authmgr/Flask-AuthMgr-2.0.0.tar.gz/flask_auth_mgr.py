#coding:utf-8
'''
* coder  : dzlua
* email  : 505544956@qq.com
* module : Flask-AuthMgr
* path   : .
* file   : flask_auth_mgr.py
* time   : 2017-11-03 13:33:54
'''
#--------------------#
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from werkzeug import security
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

import time, uuid

#--------------------#

__version__ = '2.0.0'

#--------------------#
class AuthMgrBase(object):
    def decode_password(self, password):
        if self.has_key(self, '__decode_password', 'AuthMgrBase'):
            return self.__decode_password(password)
        return security.generate_password_hash(password)
    def check_password(self, decode_password, password):
        if self.has_key(self, '__check_password', 'AuthMgrBase'):
            return self.__check_password(decode_password, password)
        return security.check_password_hash(decode_password, password)
    def generate_token(self, secret_key, expires_in, data):
        if self.has_key(self, '__generate_token', 'AuthMgrBase'):
            return self.__generate_token(secret_key, expires_in, data)
        jwt = JWT(secret_key, expires_in=expires_in)
        return jwt.dumps(data).decode('utf-8')
    def parser_token(self, secret_key, token):
        if self.has_key(self, '__parser_token', 'AuthMgrBase'):
            return self.__parser_token(secret_key, token)
        try:
            jwt = JWT(secret_key)
            return jwt.loads(token)
        except:
            return None
    #----------#
    def set_decode_password(self, fun):
        self.__decode_password = fun
        return fun
    def set_check_password(self, fun):
        self.__check_password = fun
        return fun
    def set_generate_token(self, fun):
        self.__generate_token = fun
        return fun
    def set_parser_token(self, fun):
        self.__parser_token = fun
        return fun
    #----------#
    @staticmethod
    def has_key(dict_or_obj, key, obj_class_name=None):
        if not dict_or_obj or not key:
            return False
        if isinstance(dict_or_obj, dict):
            if key in dict_or_obj:
                return True
            return False
        else:
            if key[:2] == '__':
                if not obj_class_name:
                    obj_class_name = dict_or_obj.__class__.__name__
                return hasattr(dict_or_obj,
                    '_' + obj_class_name + key)
            return hasattr(dict_or_obj, key)
    @staticmethod
    def has_keys(dict_or_obj, keys, obj_class_name=None):
        if not dict_or_obj or not keys:
            return False
        for key in keys:
            if not AuthMgrBase.has_key(dict_or_obj, key, obj_class_name):
                return False
        return True
#--------------------#
class AuthMgr(AuthMgrBase):
    def __init__(self, secret_key,
            basic_scheme='Basic', basic_realm=None,
            atoken_scheme='Bearer', atoken_realm=None, aexpires_in=600,
            rftoken_scheme='Bearer', rftoken_realm=None, rfexpires_in=3600*24,
            utoken_scheme='Bearer', utoken_realm=None, uexpires_in=1800 ):
        AuthMgrBase.__init__(self)
        #
        self.__basic = HTTPBasicAuth(scheme=basic_scheme, realm=basic_realm)
        self.__atoken = HTTPTokenAuth(scheme=atoken_scheme, realm=atoken_realm)
        self.__rftoken = HTTPTokenAuth(scheme=rftoken_scheme, realm=rftoken_realm)
        self.__utoken = HTTPTokenAuth(scheme=utoken_scheme, realm=utoken_realm)
        self.__amulti = MultiAuth(self.__basic, self.__atoken)
        self.__rfmulti = MultiAuth(self.__basic, self.__rftoken)
        #
        self.secret_key = secret_key
        self.aexpires_in = aexpires_in
        self.rfexpires_in = rfexpires_in
        self.uexpires_in = uexpires_in
        #
        self.verify_password = self.__basic.verify_password
        self.verify_access_token = self.__atoken.verify_token
        self.verify_refresh_token = self.__rftoken.verify_token
        self.verify_user_token = self.__utoken.verify_token
        #
        self.required_login = self.__basic.login_required
        self.required_access_token = self.__atoken.login_required
        self.required_refresh_token = self.__rftoken.login_required
        self.required_user_token = self.__utoken.login_required
        self.required_multi_access = self.__amulti.login_required
        self.required_multi_refresh = self.__rfmulti.login_required
        #
        self.error_handler_login = self.__basic.error_handler
        self.error_handler_access_token = self.__atoken.error_handler
        self.error_handler_refresh_token = self.__rftoken.error_handler
        self.error_handler_user_token = self.__utoken.error_handler
    #----------#
    def generate_access_token(self, data, expires_in=None):
        if expires_in is None:
            expires_in = self.aexpires_in
        tdata = {
            'data': data, 'type': 'access_token',
            'generare_time': int(time.time()),
            'expires_in': expires_in,
            'uuid': str(uuid.uuid1())
        }
        token = self.generate_token(self.secret_key, expires_in, tdata)
        if self.has_key(self, '__save_token', 'AuthMgr'):
            tdata['token'] = token
            if not self.__save_token(tdata):
                return None
        return token
    def generate_refresh_token(self, data, expires_in=None):
        if expires_in is None:
            expires_in = self.rfexpires_in
        tdata = {
            'data': data, 'type': 'refresh_token',
            'generare_time': int(time.time()),
            'expires_in': expires_in,
            'uuid': str(uuid.uuid1())
        }
        token = self.generate_token(self.secret_key, expires_in, tdata)
        if self.has_key(self, '__save_token', 'AuthMgr'):
            tdata['token'] = token
            if not self.__save_token(tdata):
                return None
        return token
    def generate_user_token(self, data, expires_in=None):
        if expires_in is None:
            expires_in = self.uexpires_in
        tdata = {
            'data': data, 'type': 'user_token',
            'generare_time': int(time.time()),
            'expires_in': expires_in,
            'uuid': str(uuid.uuid1())
        }
        token = self.generate_token(self.secret_key, expires_in, tdata)
        if self.has_key(self, '__save_token', 'AuthMgr'):
            tdata['token'] = token
            if not self.__save_token(tdata):
                return None
        return token
    def access_token_data(self, token):
        tdata = self.parser_token(self.secret_key, token)
        if not self.has_keys(tdata,
                ['type', 'data', 'expires_in', 'generare_time', 'uuid']):
            return None
        if tdata['type'] != 'access_token':
            return None
        if not self.has_key(self, '__get_token', 'AuthMgr'):
            return tdata['data']
        #
        gtoken = self.__get_token(tdata)
        if gtoken and token == gtoken:
            return tdata['data']
        return None
    def refresh_token_data(self, token):
        tdata = self.parser_token(self.secret_key, token)
        if not self.has_keys(tdata,
                ['type', 'data', 'expires_in', 'generare_time', 'uuid']):
            return None
        if tdata['type'] != 'refresh_token':
            return None
        if not self.has_key(self, '__get_token', 'AuthMgr'):
            return tdata['data']
        #
        gtoken = self.__get_token(tdata)
        if gtoken and token == gtoken:
            return tdata['data']
        return None
    def user_token_data(self, token):
        tdata = self.parser_token(self.secret_key, token)
        if not self.has_keys(tdata,
                ['type', 'data', 'expires_in', 'generare_time', 'uuid']):
            return None
        if tdata['type'] != 'user_token':
            return None
        if not self.has_key(self, '__get_token', 'AuthMgr'):
            return tdata['data']
        #
        gtoken = self.__get_token(tdata)
        if gtoken and token == gtoken:
            return tdata['data']
        return None
    #----------#
    def set_save_token(self, fun):
        self.__save_token = fun
        return fun
    def set_get_token(self, fun):
        self.__get_token = fun
        return fun
#--------------------#
