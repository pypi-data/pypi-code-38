#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Asyncio
-------

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

import asyncio

class Node:
    def __init__(self):
        self.is_running = False
        
    async def run_until_stop(self, function, *args, _sleep_time_=0, **kwargs):
        self.sleep_time = _sleep_time_
        self.is_running = True
        while self.is_running and not await function(*args, **kwargs):
            await asyncio.sleep(self.sleep_time)
            
    def stop(self):
        self.is_running = False