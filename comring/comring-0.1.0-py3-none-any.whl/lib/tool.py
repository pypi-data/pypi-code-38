from . import odoo
import logging
import os
import argparse
import configparser
import getpass
import csv
import pprint

ENCRYPTION_AVAILABLE = False

try:
    from Crypto.Cipher import AES
    from Crypto import Random
    ENCRYPTION_AVAILABLE = True
except ImportError:
    pass

ENC_KEY = b'pti-odoo-toolbox'

LOGGER = logging.getLogger(__name__)

def encrypt(text):
    if not ENCRYPTION_AVAILABLE:
        return ''
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(ENC_KEY, AES.MODE_CFB, iv)
    msg = iv + cipher.encrypt(text)
    return msg.hex()

def decrypt(message):
    if not ENCRYPTION_AVAILABLE:
        return ''
    msgbytes = bytes(bytearray.fromhex(message))
    iv = msgbytes[0:AES.block_size]
    cipher = AES.new(ENC_KEY, AES.MODE_CFB, iv)
    textbytes = cipher.decrypt(msgbytes)[len(iv):]
    return textbytes.decode()

PP = pprint.PrettyPrinter(indent=4)

def pfdebug(logger, data):
    for line in PP.pformat(data).split('\n'):
        logger.debug(line)

class SimpleTool(object):
    def __init__(self):
        self._instance = None
        self._client = None
        self._env = None

    def get_client(self):
        return self._client

    def connect(self):
        self._instance = odoo.get_instance(self._env)
        if not self._instance:
            raise Exception('Error getting instance for {}'.format(self._env))

        self._client = self._instance.connect()

    def call(self, model, method, args, kwargs):
        return self._client.call(model, method, args, kwargs)

    def search(self, model, domain, context=None, pos='all'):
        if pos == 'all':
            return self._client.search(model, domain, context)
        elif pos == 'first':
            return self._client.search_first(model, domain, context)
        elif pos == 'one':
            return self._client.search_one(model, domain, context)

    def read(self, model, ids, fields, context=None):
        return self._client.read(model, ids, fields, context)

    def read_one(self, model, single_id, fields, context=None):
        return self._client.read_one(model, single_id, fields, context)

    def search_read(self, model, domain, fields, context=None, pos='all'):
        if pos == 'all':
            return self._client.search_read(model, domain, fields, context)
        elif pos == 'first':
            return self._client.search_read_first(model, domain, fields, context)
        elif pos == 'one':
            return self._client.search_read_one(model, domain, fields, context)

    def create(self, model, data, context=None):
        return self._client.create(model, data, context)

    def write(self, model, ids, data, context=None):
        return self._client.write(model, ids, data, context)

    def csv_read(self, filename):
        result = []
        try:
            with open(filename, 'rt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    result.append(row)
        except IOError:
            LOGGER.error('Could not read %s', filename)
        return result

    def boot_add_arguments(self, parser):
        parser.add_argument('-l', '--logging', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set log level', default='WARNING')
        parser.add_argument('-e', '--env', type=str, default='devel', help='Set environment')
        parser.add_argument('-w', '--readpassword', help='Prompt for password', action='store_true')
        return True

    def boot_process_arguments(self, args):
        if args.logging:
            lvl = getattr(logging, args.logging, None)
            if isinstance(lvl, int):
                logging.getLogger().setLevel(lvl)

        self._env = args.env
        return True

    def bootstrap(self):
        odoo.load_envs(os.path.expanduser('~/.config/odoopti.yaml'))
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

        parser = argparse.ArgumentParser()
        if not self.boot_add_arguments(parser):
            LOGGER.debug('boot_add_arguments returned False')
            return False

        args = parser.parse_args()
        
        if not self.boot_process_arguments(args):
            LOGGER.debug('boot_process_arguments returned False')
            return False

        return True

