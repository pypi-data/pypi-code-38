import os
import ssl
import time
import struct
import socket
import logging
import sys
import json
from collections import defaultdict
from pprint import pprint

import xmltodict

# https://github.com/Darkfish/python-epp-client

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TESTBED_HOST = 'testbed-epp.nominet.org.uk'
OTE_HOST = 'ote-epp.nominet.org.uk'
HOST = 'epp.nominet.org.uk'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class EPPConnection(object):
    def __init__(self, host, port):
        #: Set host
        self.host = host
        self.port = port

        #: Find size of C integers
        self.format_32 = self.format_32()

        #: Create connection to EPP server
        log.info(' - Making SSL connection to {0}:{1}'.format(
            self.host,
            self.port
        ))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(301)
        self.ssl = ssl.wrap_socket(self.socket)
        print((self.host, self.port))
        self.ssl.connect((self.host, self.port))
        greeting = self.read()
        log.info("Server greeting:" + greeting.decode('utf-8'))

    def __del__(self):
        try:
            self.socket.close()
        except TypeError:
            """ Will occur when not properly connected """
            pass

    #: Uses basic EPP data structures from:
    #  - https://github.com/jochem/Python-EPP
    #  - http://www.bortzmeyer.org/4934.html
    def format_32(self):
        # Get the size of C integers. We need 32 bits unsigned.
        format_32 = ">I"
        if struct.calcsize(format_32) < 4:
            format_32 = ">L"
            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        elif struct.calcsize(format_32) > 4:
            format_32 = ">H"
            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        else:
            pass
        return format_32

    def int_from_net(self, data):
        return struct.unpack(self.format_32, data)[0]

    def int_to_net(self, value):
        return struct.pack(self.format_32, value)

    def read(self, schema_critical=True):
        log.debug('  - Trying to read 4-byte header from socket')
        length = self.ssl.read(4)
        if length:
            i = self.int_from_net(length)-4
            log.debug(
                '  - Found length header, trying to read {0} bytes'.format(i)
            )

            #: Return raw data
            return(self.ssl.read(i))

    def write(self, xml):
        epp_as_string = xml
        # +4 for the length field itself (section 4 mandates that)
        # +2 for the CRLF at the end
        length = self.int_to_net(len(epp_as_string) + 4 + 2)
        log.debug(
            'Sending XML ({0} bytes):\n'.format(
                len(epp_as_string) + 4 + 2) + xml
        )
        self.ssl.send(length)

        return self.ssl.send("{}\r\n".format(epp_as_string).encode('utf-8'))

class EPP:
    def __init__(self, epp_connection):
        self.epp_connection = epp_connection

    def _parse_response(self, data):
       resp_dict = defaultdict(dict)
       key_list = (msg_key, reason_key, avail_key, code_key) = 'msg', 'reason', '@avail', '@code'

       # resp_dict.update(
       #     dict(cmd='{}.xml'.format(args.cmd.replace('-', '_')), domain=args.domain, server=args.server, resp_key_list=[x for x in data.keys() if '.xml' in x])
       # )

       if 'response' in data['epp']:
           response = data['epp']['response']
           result = response['result']

           msg = result.get(msg_key)
           code = result.get(code_key)
           reason = result.get('extValue', {}).get(reason_key)
           avail_status = response.get('resData', {}).get('domain:chkData', {}).get('domain:cd', {}).get('domain:name',
                                                                                                         {}).get(avail_key)

           for f_name, raw_out in data.items():
               for item in zip((key_list), (msg, reason, avail_status, code)):
                   k, v = item
                   if v:
                       resp_dict[f_name][k] = v
                       # log.info('{0:<20} {1}'.format(f_name, v))
       else:
           resp_dict['epp'] = None

       return resp_dict['epp']

    def _write(self, data):
        return self.epp_connection.write(data)

    def _read(self):
        return self.epp_connection.read().decode('utf-8')

    def _send_xml(self, action, **params):
        result = defaultdict(list)
        print('{1}\nProcessing {0}\n{1}'.format(action, 32 * '='))
        fp = os.path.join(ROOT_DIR, "templates", '{}.xml'.format(action))
        with open(fp, 'r') as f:
            log.debug('Sending {0}'.format(fp))
            processed_data = f.read().format(**params)
            # print(processed_data)
            self._write(processed_data)
#            time.sleep(1)
            resp = self._read()
            #log.debug('Response from server: \n{0}'.format(resp))
            # print('Response from server: \n{0}'.format(resp))
            result = xmltodict.parse(resp)
        return self._parse_response(result)

    def login(self, user, password):
        return self._send_xml('login', USER=user, PASSWORD=password)

    def hello(self):
        return self._send_xml('hello')

    def domain_delete(self, domain, user):
        return self._send_xml('domain_delete', DOMAIN=domain, USER=user)

    def domain_create(self, domain, user, password):
        return self._send_xml('domain_create', DOMAIN=domain, USER=user, PASSWORD=password, DOMAIN_PERIOD=2)

    def domain_check(self, domain, user):
        return self._send_xml('domain_check', DOMAIN=domain, USER=user)

    def contact_update(self, domain):
        return self._send_xml('contact_update')

    def contact_check(self, user):
        return self._send_xml('contact_check', USER=user)

    def contact_create(self, user, name, company, street1, street2, city, country, postcode, country_code, phone, email):
        return self._send_xml('contact_create', USER=user, NAME=name, COMPANY=company, STREET1=street1, STREET2=street2, CITY=city, COUNTRY=country, POST_CODE=postcode, COUNTRY_CODE=country_code, PHONE=phone, EMAIL=email)
