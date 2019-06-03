# -*- coding: utf8 -*-

from basicauth import encode
#import keyring
import configparser
from .constants import USERDATA_PATH


def get_header_basic_auth():
    headers = {
        "authorization": get_encoded_string(),
        "x-account-uuid": get_account_uuid(),
        "token": get_token()
    }

    return headers


def get_encoded_string():
    config = configparser.ConfigParser()
    config.read(USERDATA_PATH)
    username = config.get('default', 'username')
    account_uuid = config.get('default', 'account-uuid')
    password = config.get('default', 'password')
    encoded_str = encode(username, password)

    return encoded_str

def get_token():
    config = configparser.ConfigParser()
    config.read(USERDATA_PATH)
    token = config.get('default', 'token')
    return token 


def get_account_uuid():

    config = configparser.ConfigParser()
    config.read(USERDATA_PATH)
    account_uuid = config.get('default', 'account-uuid')

    return account_uuid
