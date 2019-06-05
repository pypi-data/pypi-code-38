#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Tornado
-------

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

import asyncio, json
import tornado.web, tornado.websocket
from .asyncio import Node

class WebApplication(tornado.web.Application, Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self)
        super().__init__(*args, **kwargs)
        
        
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, clients={}, is_binary=False, is_nodelay=False, **kwargs):
        super().__init__(*args, **kwargs)
        if clients:
            self.clients = clients
        else:
            self.application.__dict__.setdefault('clients', {})
            self.clients = self.application.clients
        self.is_binary = is_binary
        self.is_nodelay = is_nodelay
        
    def open(self, uri, **kwargs):
        self.set_nodelay(self.is_nodelay)
        self.clients[self] = uri
        
    def on_close(self):
        self.clients.pop(self, None)
        
    def write_message(self, message, binary=False, **kwargs):
        if isinstance(message, dict):
            message = json.dumps(message, **kwargs).replace("</", "<\\/")
        try:
            return super().write_message(message, binary=binary)
        except tornado.websocket.WebSocketClosedError:
            self.on_close()
            
            
class WebSocketClient:
    def __init__(self, url, is_reconnect=True):
        self.reconnect_sleep_time = 1.0
        self.connect_timeout = None
        self.connect_key_arguments = {}
        self.connection = None
        self.is_running = False
        self.url = url
        self.is_reconnect = is_reconnect
        
    def on_connect_success(self):
        pass
        
    def on_connect_refused(self):
        pass
        
    def on_connect_timeout(self):
        pass
        
    def check_message(self, message):
        if not message: self.on_close()
        
    def create_message_callback(self, on_message_callback):
        def on_message(message):
            self.check_message(message)
            on_message_callback(message)
        return on_message
        
    async def connect(self, on_message_callback=None, **kwargs):
        callback = on_message_callback and self.create_message_callback(on_message_callback)
        return await tornado.websocket.websocket_connect(self.url, on_message_callback=callback, **kwargs)
        
    async def connect_until_made(self, sleep_time=1.0, timeout=None, on_success=None, on_refused=None, on_timeout=None, **kwargs):
        self.reconnect_sleep_time = sleep_time
        self.connect_timeout = timeout
        self.on_connect_success = on_success or self.on_connect_success
        self.on_connect_refused = on_refused or self.on_connect_refused
        self.on_connect_timeout = on_timeout or self.on_connect_timeout
        self.connect_key_arguments = kwargs
        self.is_running = True
        loop = asyncio.get_event_loop()
        end_time = loop.time() + sleep_time
        while self.is_running and self.is_reconnect:
            # Use loop.time() and asyncio.sleep() here because its timing is wrong in LXD
            if loop.time() < end_time:
                await asyncio.sleep(sleep_time)
            try:
                self.connection = await asyncio.wait_for(self.connect(**kwargs), timeout)
            except ConnectionRefusedError:
                self.on_connect_refused()
            except asyncio.TimeoutError:
                self.on_connect_timeout()
                break
            # Catch exceptions for LXD container to keep running
            except (tornado.iostream.StreamClosedError, tornado.simple_httpclient.HTTPStreamClosedError, ConnectionResetError):
                pass
            else:
                self.on_connect_success()
                break
                
    def disconnect(self):
        if self.connection: self.connection.close()
        self.connection = None
        self.is_running = False
        
    def reconnect(self):
        self.disconnect()
        if self.is_reconnect:
            future = self.connect_until_made(self.reconnect_sleep_time, self.connect_timeout, self.on_connect_success, self.on_connect_refused, self.on_connect_timeout, **self.connect_key_arguments)
            asyncio.ensure_future(future)
        else:
            return asyncio.ensure_future(self.connect(self.connect_key_arguments))
            
    def on_close(self):
        self.disconnect()
        if self.is_reconnect:
            future = self.connect_until_made(self.reconnect_sleep_time, self.connect_timeout, self.on_connect_success, self.on_connect_refused, self.on_connect_timeout, **self.connect_key_arguments)
            asyncio.ensure_future(future)
            
    async def read_message(self):
        if not self.connection: return
        message = await self.connection.read_message()
        if not message: self.on_close()
        return message
