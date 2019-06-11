import asyncio
import queue
import sys
from networktools.colorprint import gprint, bprint, rprint
from networktools.queue import send_queue, read_queue_gen
from networktools.queue import send_async_queue, read_async_queue
from networktools.library import my_random_string


class Channel:
    def __init__(self, *args, **kwargs):
        id_length = kwargs.get('id_length', 4)
        self.id_ch = my_random_string(id_length)
        self.queue_a2b = queue.Queue()
        self.queue_b2a = queue.Queue()

    def set_id(self, id_ch):
        self.id_ch = id_ch

    def get_id(self):
        return self.id_ch

    def get_channel(self):
        return (self.queue_a2b, self.queue_b2a)

    def switch_queue(self, here='a'):
        queue = self.queue_a2b
        if here == 'b':
            queue = self.queue_b2a
        return queue

    def send_msg(self, msg, here='a'):
        queue = self.switch_queue(here)
        send_queue(queue, msg)

    def recv_msg(self, here='a'):
        queue = self.switch_queue(here)
        for msg in read_queue_gen(queue):
            yield msg


class AsyncChannel:
    def __init__(self, *args, **kwargs):
        id_length = kwargs.get('id_length', 4)
        self.id_ch = my_random_string(id_length)
        self.queue_a2b = asyncio.Queue()
        self.queue_b2a = asyncio.Queue()

    def set_id(self, id_ch):
        self.id_ch = id_ch

    def get_id(self):
        return self.id_ch

    def get_channel(self):
        return (self.queue_a2b, self.queue_b2a)

    def switch_queue(self, here='a'):
        queue = self.queue_a2b
        if here == 'b':
            queue = self.queue_b2a
        return queue

    async def send_msg(self, msg, here='a'):
        queue = self.switch_queue(here)
        await send_async_queue(queue, msg)

    async def recv_msg(self, here='a'):
        queue = self.switch_queue(here)
        async for msg in read_async_queue(queue):
            yield msg
