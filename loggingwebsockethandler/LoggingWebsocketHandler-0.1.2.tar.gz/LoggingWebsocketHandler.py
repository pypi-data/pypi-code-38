# -*- coding: utf-8 -*-
import logging
from queue import Queue
import threading
import traceback

import websocket


class WebsocketHandler(logging.Handler):

    def __init__(self, url):
        logging.Handler.__init__(self)
        self.queue = queue = Queue()
        self.client = Websocket(url, queue)
        self.client.start()

    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)


class Websocket:

    def __init__(self, url, queue):
        self.client = None
        self.queue = queue
        self.url = url
        self.thread = None

    def start(self):
        self.thread = thread = threading.Thread(target=self.main)
        thread.setDaemon(True)
        thread.start()

    def main(self):
        while True:
            self.loop()

    def loop(self):
        try:
            self.conn = websocket.create_connection(self.url)

            while True:
                msg = self.queue.get()
                self.conn.send(msg)
        except Exception as ex:
            traceback.print_exc()
