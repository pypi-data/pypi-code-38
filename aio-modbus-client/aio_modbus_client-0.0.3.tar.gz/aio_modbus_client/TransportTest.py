from .Transport import Transport
import asyncio


class TransportSocket(Transport):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_answer = 0
        self.current_byte = 0
        self.answer = []

    async def connect(self):
        return True

    async def write(self, data):
        # result = self.answer[self.current_answer]
        self.current_answer += 1
        self.current_byte = 0
        return

    async def read(self, size):
        result = self.answer[self.current_answer][self.current_byte: size]
        self.current_byte += size
        return result
