import asyncio
import queue
from networktools.colorprint import gprint, bprint, rprint


def read_queue(queue, actions, qtimer=None):
    """
    msg_in = {'command':<some_command>, 'data_opts':{<some_dict>}}
    qtimer a qtimer instance
    """
    result = []
    try:
        if not queue.empty():
            for i in range(queue.qsize()):
                msg_in = queue.get()
                command = msg_in.get('command')
                if command in actions:
                    result_item = actions.get(command)(
                        **msg_in.get('data_opts'))
                    yield result_item
                if qtimer:
                    qtimer.stop()
            return result
    except Exception as ex:
        print("Error con modulo de escritura de cola")
        raise ex


def send_queue(queue, value, join=False):
    print("Sending data by queue", value)
    if queue:
        queue.put(value)
        if join:
            queue.join()


def read_queue_gen(queue, fn_name=None):
    # generator
    try:
        if not queue.empty():
            # block until process the list
            for i in range(queue.qsize()):
                msg_in = queue.get()
                yield msg_in
                queue.task_done()
    except Exception as ex:
        print("Error <%s>con modulo de escritura de queue, en funcion <%s>" % (
            ex, fn_name))
        raise ex


async def send_async_queue(queue, value, join=False):
    gprint("Sending data by async queue...>", value)
    await queue.put(value)
    if join:
        await queue.join()


async def read_async_queue(queue, fn_name=None):
    # generator
    print("Queue empty", queue.empty(), queue.qsize())
    await asyncio.sleep(.5)
    try:
        if not queue.empty():
            # block until process the list
            for i in range(queue.qsize()):
                msg_in = await queue.get()
                yield msg_in
                await asyncio.sleep(0.2)
                queue.task_done()
    except Exception as ex:
        print("Error <%s>con modulo de escritura de async queue, en funcion <%s>" % (
            ex, fn_name))
        raise ex
