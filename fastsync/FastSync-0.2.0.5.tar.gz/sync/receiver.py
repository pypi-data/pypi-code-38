#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Muduo
'''
    FastSync Receiver
'''
import web
import sys
import os
import shutil
import logging
import json
from base64 import b64decode

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(filename)s -> (%(threadName)s) [%(funcName)s line:%(lineno)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

urls = (
    ('/(.*)', 'index')
)


def write_file_by_b64(path, content):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    try:
        with open(path, 'wb') as f:
            f.write(b64decode(content))
    except Exception as e:
        logging.info(e)

class index:
    
    def GET(self, path):
        return 'FastSync Receiving ...'

    def POST(self, path):
        return json.dumps(self.__POST(path))

    def __POST(self, path):
        try:
            data = web.input()
            if data.get('secret_key') != web.secret_key:
                return {
                    'status': 1,
                    'msg': 'auth fail',
                }

            if path == 'create':
                if data.get('is_directory') == 'true':
                    if not os.path.exists(data.get('path')):
                        os.makedirs(data.get('path'))
                        logging.info('[Create] DIR %s' % data.get('path'))
                else:
                    write_file_by_b64(data.get('path'), data.get('data'))
                    logging.info('[Create] FILE %s' % data.get('path'))
            elif path == 'move':
                shutil.move(data.get('fpath'), data.get('tpath'))
                logging.info('[Move] %s -> %s' % (data.get('fpath'), data.get('tpath')))
            elif path == 'delete':
                if data.get('is_directory') == 'true':
                    shutil.rmtree(data.get('path'))
                    logging.info('[Delete] DIR %s' % data.get('path'))
                else:
                    os.remove(data.get('path'))
                    logging.info('[Delete] FILE %s' % data.get('path'))
            elif path == 'modify':
                if data.get('is_directory') == 'true':
                    if not os.path.exists(data.get('path')):
                        os.makedirs(data.get('path'))
                        logging.info('[Modify] DIR %s' % data.get('path'))
                else:
                    write_file_by_b64(data.get('path'), data.get('data'))
                    logging.info('[Modify] FILE %s' % data.get('path'))
            else:
                return {
                    'status': 1,
                    'msg': 'not found'
                }
        except Exception as e:
            return {
                'status': 1,
                'msg': str(e),
            }
        
        return {
            'status': 0,
            'msg': '',
        }

def receiving(port, secret_key):
    del sys.argv[1:]
    sys.argv.append(str(port))
    web.secret_key = secret_key
    app = web.application(urls, globals())
    app.run()

if __name__ == "__main__":
    receiving('8500', '')