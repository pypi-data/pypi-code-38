#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Muduo
'''
    FastSync Sender
'''

import os
import time
import requests
import platform
import logging
import signal
from urlparse import urlparse
from base64 import b64encode
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileCreatedEvent

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(filename)s -> (%(threadName)s) [%(funcName)s line:%(lineno)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def read_file_as_b64(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

            # 不能大于1M
            if len(content) > 1 * 1024 * 1024:
                return None

            return b64encode(content)
    except Exception as e:
        logging.info(e)
    return None

class SenderHandler(FileSystemEventHandler):

    def __init__(self, send_path, receive_uri, secret_key, patterns):
        FileSystemEventHandler.__init__(self)
        self.send_path = send_path.rstrip('/')
        result = urlparse(receive_uri)
        self.server = '%s://%s' % (result.scheme, result.netloc)
        if 'Windows' in platform.system():
            self.receive_path = result.path.strip('/')
        else:
            self.receive_path = result.path.rstrip('/')
        self.secret_key = secret_key
        self.patterns = patterns

    def on_created(self, event):
        if self.ignore(event):
            return

        try:
            logging.info('[Create] %s %s' % ('DIR' if event.is_directory else 'FILE', self.mapping(event.src_path)))
            if event.is_directory:
                response = requests.post('%s/create' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'is_directory': 'true',
                }).json()
            else:
                data = read_file_as_b64(event.src_path)
                if data == None:
                    return

                response = requests.post('%s/create' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'data': data,
                }).json()
            if response['status'] == 0:
                logging.info('[Create] Success')
            else:
                logging.info('[Create] Fail %s' % response['msg'])
        except Exception as e:
            logging.fatal(e)

    def on_moved(self, event):
        if self.ignore(event):
            return

        try:
            logging.info('[Move] %s %s -> %s' % ('DIR' if event.is_directory else 'FILE', self.mapping(event.src_path), self.mapping(event.dest_path)))
            response = requests.post('%s/move' % self.server, data={
                'secret_key': self.secret_key,
                'fpath': self.mapping(event.src_path),
                'tpath': self.mapping(event.dest_path),
            }).json()
            if response['status'] == 0:
                logging.info('[Move] Success')
            else:
                logging.info('[Move] Fail %s' % response['msg'])
        except Exception as e:
            logging.fatal(e)

    def on_deleted(self, event):
        if self.ignore(event):
            return

        try:
            logging.info('[Delete] %s %s' % ('DIR' if event.is_directory else 'FILE', self.mapping(event.src_path)))
            if event.is_directory:
                response = requests.post('%s/delete' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'is_directory': 'true',
                }).json()
            else:
                response = requests.post('%s/create' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'is_directory': 'false',
                }).json()
            if response['status'] == 0:
                logging.info('[Delete] Success')
            else:
                logging.info('[Delete] Fail %s' % response['msg'])
        except Exception as e:
            logging.fatal(e)

    def on_modified(self, event):
        if self.ignore(event):
            return

        try:
            logging.info('[Modify] %s %s' % ('DIR' if event.is_directory else 'FILE', self.mapping(event.src_path)))
            if event.is_directory:
                response = requests.post('%s/modify' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'is_directory': 'true',
                }).json()
            else:
                data = read_file_as_b64(event.src_path)
                if data == None:
                    return

                response = requests.post('%s/modify' % self.server, data={
                    'secret_key': self.secret_key,
                    'path': self.mapping(event.src_path),
                    'data': data,
                }).json()
            if response['status'] == 0:
                logging.info('[Modify] Success')
            else:
                logging.info('[Modify] Fail %s' % response['msg'])
        except Exception as e:
            logging.fatal(e)

    def mapping(self, path):
        return path.replace(self.send_path, self.receive_path)

    def ignore(self, event):

        for pattern in self.patterns:
            if event.src_path.find(pattern) != -1:
                return True

        return False

def sending(send_path, receive_uri, secret_key, patterns):
    sender_handler = SenderHandler(send_path, receive_uri, secret_key, patterns)

    def start_observer():
        observer = Observer()
        observer.schedule(
            sender_handler,
            send_path,
            recursive=True
        )
        observer.start()
        logging.info('start sync path: %s -> %s' % (send_path, receive_uri))

        return observer
    
    observer = start_observer()

    def sync_all(signum, fram):
        for parent, dirnames, filenames in os.walk(send_path):
            for filename in filenames:
                path = os.path.join(parent, filename)
                event = FileCreatedEvent(path)
                sender_handler.on_created(event)

    signal.signal(signal.SIGALRM, sync_all)
    
    while True:
        if not observer.isAlive():
            observer.stop()
            observer = start_observer()
        time.sleep(3)

if __name__ == '__main__':
    sending('/Users/test/tmp/1', 'http://127.0.0.1:8500/Users/test/tmp/2', '', ['.git', '.svn'])
