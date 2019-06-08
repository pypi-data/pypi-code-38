''' an example service '''
import asyncio
import time
from bluemax import context

async def clock():
    ''' Will broadcast every 5 seconds '''
    while True:
        context.broadcast('time', {'now': time.time()})
        await asyncio.sleep(5)
