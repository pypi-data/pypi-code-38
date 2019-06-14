#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

END_OF_MESSAGE = "[END_OF_MESSAGE]"

HOMEVEE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#DATA_DIR = os.path.join(HOMEVEE_DIR, 'data')
DATA_DIR = os.path.abspath(os.path.join(os.sep, 'homevee_data', 'data'))

#make data dir if not exists
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)

SSL_FULLCHAIN = os.path.join(DATA_DIR, 'fullchain.pem')
SSL_CERT = os.path.join(DATA_DIR, 'cert.pem')

LOCAL_SSL_PRIVKEY = os.path.join(DATA_DIR, 'local_privkey.pem')
LOCAL_SSL_CERT = os.path.join(DATA_DIR, 'local_cert.pem')
CLOUD_SSL_CERT = os.path.join(DATA_DIR, 'cloud_cert.pem')

HOMEVEE_VERSION_NUMBER = "0.1.1.35"