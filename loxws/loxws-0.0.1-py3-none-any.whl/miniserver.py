"""Represent the miniserver."""

import asyncio
import logging
import datetime
import binascii
import urllib.parse

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import HMAC, SHA1
from Crypto.Util.Padding import pad, unpad
from requests import codes, get, utils
from base64 import b64decode, b64encode

from .messageheader import MessageHeader
from .messagebody import MessageBody

from .configdata import ConfigData

_LOGGER = logging.getLogger(__name__)

class Miniserver:
    """This class connects to the Loxone Miniserver."""

    def __init__(self, host=None, port=None, username=None, password=None, publickey=None, privatekey=None, key=None, iv=None):
        """Initialize Miniserver class."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.message_header = None
        self.message_body = None
        self.client_salt_count = 0
        self.client_salt = self.generate_client_salt()
        self.public_key = RSA.importKey(publickey)
        self.private_key = privatekey
        self.key = key
        self.iv = iv
        self.config_data = None
        self.ready = asyncio.Event()
        self.waiting_for_response = False

    def connect(self, loop, connection_status):
        """Connect to the miniserver."""
        _LOGGER.debug("connect")
        from .wsclient import WSClient
        self.loop = loop
        self.async_connection_status_callback = connection_status

        self.wsclient = WSClient(self.loop, self.host, self.port, self.username, self.password, self.async_session_handler, self.async_message_handler)
        self.wsclient.start()

        _LOGGER.debug("Finished connect")
        
    def shutdown(self):
        self.wsclient.stop()

    async def wait_until_ready(self):
        await self.ready.wait()
        self.loop.create_task(self.keep_alive())

    def async_session_handler(self, state):
        _LOGGER.debug("async_session_handler")
        _LOGGER.debug("state: {0}".format(state))
        if state == 'running':
            command = "jdev/sys/keyexchange/" + self.private_key
            self.wsclient.send(command)

    def async_message_handler(self, message, isBinary):
        #_LOGGER.debug("async_message_handler")
        if isBinary:
            #_LOGGER.debug("RECV BINARY MESSAGE: {0} bytes".format(len(message)))
            if len(message) == 8 and message[0] == 3:
                #_LOGGER.debug('HEADER')
                self.message_header = MessageHeader(message)
            else:
                #_LOGGER.debug('BINARY DATA')
                self.message_body = MessageBody(message, True, self.message_header, self.config_data)

        else:
            #_LOGGER.debug("RECV TEXT MESSAGE: {0}".format(message))

            if message.startswith("{"):
                self.message_body = MessageBody(message, False, self.message_header, self.config_data)
            else:
                self.message_body = MessageBody(self.decrypt_message(message), False, self.message_header, self.config_data)

            if "keyexchange" in self.message_body.control:
                _LOGGER.debug('PROCESS keyexchange response')
                command = "jdev/sys/getkey2/" + self.username
                _LOGGER.debug("SEND COMMAND: " + command)
                self.wsclient.send(self.encrypt_command(command))

            elif "getkey2" in self.message_body.control:
                _LOGGER.debug('PROCESS getkey2 response')
                self.server_key = self.message_body.msg["LL"]["value"]["key"]
                #_LOGGER.debug("  server_key: {0} {1}".format(type(self.server_key), self.server_key))
                self.server_salt = self.message_body.msg["LL"]["value"]["salt"]
                #_LOGGER.debug("  server_salt: {0} {1}".format(type(self.server_salt), self.server_salt))

                #_LOGGER.debug('  Hash user password')
                hash_sha = SHA1.new()
                hash_sha.update(bytes('{0}:{1}'.format(
                    self.password,
                    self.server_salt),'utf-8'))
                pwhash = hash_sha.hexdigest().upper()

                #_LOGGER.debug('  Hash credential')
                hash_hmac = HMAC.new(binascii.a2b_hex(self.server_key), digestmod=SHA1)
                hash_hmac.update(bytes('{0}:{1}'.format(
                    self.username,
                    pwhash),'utf-8'))
                hash = hash_hmac.hexdigest()

                permissions = "4"
                uuid = "098802a2-02b4-603c-ffffeee000d80cfd"
                info = "LoxHome"
                command = "jdev/sys/gettoken/{0}/{1}/{2}/{3}/{4}".format(hash, self.username, permissions, uuid, info)
                _LOGGER.debug("SEND COMMAND: " + command)
                self.wsclient.send(self.encrypt_command(command))

            elif "gettoken" in self.message_body.control:
                _LOGGER.debug('PROCESS gettoken response')
                command = "data/LoxAPP3.json"
                _LOGGER.debug("SEND COMMAND: " + command)
                self.wsclient.send(command)

            elif "LoxAPP3.json" in self.message_body.control:
                _LOGGER.debug('PROCESS LoxAPP3.json response')
                self.config_data = ConfigData(self.message_body.msg)
                command = "jdev/sps/enablebinstatusupdate"
                _LOGGER.debug("SEND COMMAND: " + command)
                self.ready.set()
                self.wsclient.send(self.encrypt_command(command))

            elif "enablebinstatusupdate" in self.message_body.control:
                _LOGGER.debug('PROCESS enablebinstatusupdate response')

            elif "dev/sps/io/" in self.message_body.control:
                _LOGGER.debug('PROCESS io response')
                _LOGGER.debug("response: " + self.decrypt_message(message))

            else:
                _LOGGER.debug('PROCESS <UNKNOWN> response')
                _LOGGER.debug("header: {0}-{1}-{2}".format(self.message_header.payload[0], self.message_header.payload[1], self.message_header.payload[2]))
                _LOGGER.debug("response: " + self.decrypt_message(message))

        self.waiting_for_response = False

    def send_command(self, command):
        self.wsclient.send(self.encrypt_command(command))

    async def send_command_with_response(self, command):
        while self.waiting_for_response == True:
            await asyncio.sleep(0.2)

        self.waiting_for_response = True
        self.wsclient.send(self.encrypt_command(command))

    async def keep_alive(self):
        while self.loop.is_running():
            await asyncio.sleep(60)
            command = 'keepalive'
            #_LOGGER.debug("SEND COMMAND: " + command)
            self.wsclient.send(command) 

    def encrypt_command(self, command):
        salted_command = "salt/{0}/{1}".format(self.client_salt, command) 
        _LOGGER.debug("  salted_command: {0}".format(salted_command))

        key = binascii.unhexlify(self.key)
        iv = binascii.unhexlify(self.iv)
        cipher_aes = AES.new(key, AES.MODE_CBC, iv)

        length = len(salted_command)
        #_LOGGER.debug("  length: {0} {1}".format(type(length), length))
        padding_len = AES.block_size - (length % AES.block_size)
        #_LOGGER.debug("  padding_len: {0} {1}".format(type(padding_len), padding_len))
        padding = "\x00" * padding_len
        #_LOGGER.debug("  salted_command: {0} {1}".format(type(salted_command), salted_command))
        #_LOGGER.debug("  padding: {0} {1}".format(type(padding), padding))
        padded_salted_command = salted_command + padding

        #enc_cmd_part = cipher_aes.encrypt(pad(salted_command.encode('utf8'), AES.block_size))
        enc_cmd_part = cipher_aes.encrypt(bytes(padded_salted_command, 'utf-8'))
        #_LOGGER.debug("  enc_cmd_part: {0} {1}".format(type(enc_cmd_part), enc_cmd_part))

        b64enc = b64encode(enc_cmd_part)
        #_LOGGER.debug("  b64enc: {0} {1}".format(type(b64enc), b64enc))

        #b64enc_quote = utils.quote(b64encode(enc_cmd_part))
        #_LOGGER.debug("  b64enc_quote: {0} {1}".format(type(b64enc_quote), b64enc_quote))

        urlencoded = urllib.parse.quote(b64enc, safe='')
        #_LOGGER.debug("  urlencoded: {0} {1}".format(type(urlencoded), urlencoded))

        encrypted_command = "jdev/sys/fenc/{0}".format(urlencoded) #.encode('utf8')
        #_LOGGER.debug("  encrypted_command: {0}".format(encrypted_command))

        return encrypted_command
    
    def decrypt_message(self, message):
        m = message
        #_LOGGER.debug("  m type: {0}".format(type(m)))

        cmd = b64decode(m)
        #_LOGGER.debug("  cmd type: {0}".format(type(cmd)))
       
        key = binascii.unhexlify(self.key)
        iv = binascii.unhexlify(self.iv)
        cipher_aes = AES.new(key, AES.MODE_CBC, iv)

        r = (cipher_aes.decrypt(cmd), AES.block_size)[0]
        #_LOGGER.debug("  r: {0} |{1}|".format(type(r), r))

        while r.endswith(b'\x00'):
            r = r[:-1]

        #_LOGGER.debug("  decrypted_message: |{0}|".format(r))
        return str(r,'utf8')

    def generate_client_salt(self):
        #_LOGGER.debug("Generate Client Salt")
        self.client_salt_count = self.client_salt_count + 1
        salt = format(str(self.client_salt_count), "a>4s") + "123e"
        #salt = "123e"
        _LOGGER.debug("  salt = " + salt)
        return salt