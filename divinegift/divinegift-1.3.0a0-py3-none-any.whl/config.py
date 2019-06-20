from divinegift.logger import log_info, log_err, log_warning
from divinegift.cipher import read_key, get_cipher, encrypt_str, decrypt_str, get_key, write_key, decode_password, encode_password
import divinegift.main as dmain
#########################################################################
import sys
import os
from datetime import datetime

class EmptyConfig(Exception):
    pass


class Settings:
    parse_settings_cnt = 0
    def __init__(self):
        self.settings = {}
        self.cipher_key = None

    def get_settings(self):
        return self.settings

    def set_settings(self, json_str: object):
        self.settings = json_str

    def parse_settings(self, file_: str = './settings.ini', encoding: str = 'utf-8',
                       log_changes: bool = True, use_yaml=True, ignore_parse_cnt=False):
        """
        Parse settings from file_
        :param file_: Filename with settings
        :param encoding: Encoding
        :return: None
        """
        if not ignore_parse_cnt:
            self.__class__.parse_settings_cnt += 1
            if self.__class__.parse_settings_cnt > 2:
                raise EmptyConfig('Settings not parsed. Is there any data?')
        
        if use_yaml:
            c = dmain.Yaml(file_, encoding=encoding)
        else:
            c = dmain.Json(file_, encoding=encoding)

        json_data = c.parse()

        if log_changes and json_data:
            dict_c = dmain.dict_compare(self.settings, json_data)
            added, removed, modified, same = dict_c.values()
            if len(added) > 0:
                for r in list(added):
                    log_warning(f'Added {r}: {json_data.get(r)}')
            if len(removed) > 0:
                for r in list(removed):
                    log_warning('Removed {}: {}'.format(r, self.settings.get(r)))
            if len(modified) > 0:
                for r in list(modified):
                    log_warning('Modified {}: {} -> {}'.format(r, modified.get(r)[0], modified.get(r)[1]))
        elif log_changes and not json_data:
            try:
                self.convert_config(file_, file_, encoding=encoding, use_yaml=use_yaml)
                self.parse_settings(file_, encoding, use_yaml)
            except EmptyConfig as ms:
                log_err(ms)
                sys.exit(-1)
            except Exception as ex:
                raise Exception('Settings not parsed. Is there any data 2?')

        self.set_settings(json_data)

    def initialize_cipher(self, ck_fname: str = 'key.ck'):
        self.cipher_key = get_key()
        write_key(ck_fname, self.cipher_key)

    def encrypt_password(self, conn_name: str, ck_fname: str = 'key.ck'):
        if not self.cipher_key:
            self.cipher_key = read_key(ck_fname)
            if not self.cipher_key:
                self.initialize_cipher()
        cipher = get_cipher(self.cipher_key)
        self.settings[conn_name]['db_pass'] = encrypt_str(self.settings[conn_name]['db_pass'], cipher)

    def decrypt_password(self, conn_name: str, ck_fname: str = 'key.ck'):
        if not self.cipher_key:
            self.cipher_key = read_key(ck_fname)
        cipher = get_cipher(self.cipher_key)
        self.settings[conn_name]['db_pass'] = decrypt_str(self.settings[conn_name]['db_pass'], cipher)

    def encode_password(self, conn_name: str):
        settings = self.get_settings().copy()
        settings[conn_name]['db_pass'] = encode_password(settings[conn_name]['db_pass'])
        self.set_settings(settings)

    def decode_password(self, conn_name: str):
        settings = self.get_settings().copy()
        settings[conn_name]['db_pass'] = decode_password(settings[conn_name]['db_pass'])
        self.set_settings(settings)

    def save_settings(self, file_: str = './settings.ini', encoding='utf-8', use_yaml=True):
        if use_yaml:
            c = dmain.Yaml(file_, encoding=encoding)
        else:
            c = dmain.Json(file_, encoding=encoding)
        c.set_data(self.get_settings())
        c.create()

    @staticmethod
    def convert_config(file_from: str = './settings.ini', file_to: str = './settings.ini',
                       encoding='utf-8', use_yaml=True):
        if use_yaml:
            j = dmain.Json(file_from, encoding=encoding)
            y = dmain.Yaml(file_to, encoding=encoding)
            j.parse()
            y.set_data(j.get_data())
            y.create()
        else:
            y = dmain.Yaml(file_from, encoding=encoding)
            j = dmain.Json(file_to, encoding=encoding)
            y.parse()
            j.set_data(y.get_data())
            j.create()

    @staticmethod
    def get_version(fname=None):
        if not fname:
            fname = sys.argv[0]
        filename = dmain.get_list_files(os.path.dirname(fname), filter=os.path.basename(fname), add_path=True)[-1]
        version = datetime.fromtimestamp(os.path.getmtime(filename))
        return datetime.strftime(version, '%y%m%d')


if __name__ == '__main__':
    pass
