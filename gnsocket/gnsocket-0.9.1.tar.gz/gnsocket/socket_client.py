import socket
from networktools.queue import read_queue_gen
from gnsocket.gn_socket import GNCSocket
# Standar lib
import asyncio
import functools
from multiprocessing import Manager, Queue, Lock

# contrib modules
import ujson as json

# Own module
from gnsocket.gn_socket import GNCSocket
from gnsocket.socket_base import GNCSocketBase

# module tasktools
from tasktools.taskloop import coromask, renew, simple_fargs
from networktools.colorprint import gprint, bprint, rprint

from networktools.library import pattern_value, \
    fill_pattern, context_split, \
    gns_loads, gns_dumps
from networktools.library import my_random_string

import ujson as json

tsleep = 2


class GNCSocketClient(GNCSocketBase):

    def __init__(self, queue_n2t, queue_t2n, *args, **kwargs):
        super().__init__(queue_n2t, queue_t2n, 'client', *args, **kwargs)
        bprint("=="*30)
        rprint("(write) n2t->%s" % queue_n2t)
        rprint("(read) t2n->%s" % queue_t2n)
        bprint("=="*30)
        self.set_socket_task(self.socket_task)

    def socket_task(self):
        # client socket
        gprint("=#="*20)
        rprint("Socket tasks: (writer, reader)")
        gprint("=#="*20)
        loop = asyncio.get_event_loop()
        with GNCSocket(mode='client') as gs:
            try:
                self.loop = loop
                gs.set_address(self.address)
                gs.set_loop(loop)
                gprint("=#="*20)
                bprint("Inicializando client")
                gprint("=#="*20)

                async def socket_io():
                    idc = await gs.create_client()
                    try:
                        args = [gs, idc]
                        task_1 = loop.create_task(
                            coromask(
                                self.sock_read,
                                args,
                                simple_fargs)
                        )
                        task_1.add_done_callback(
                            functools.partial(
                                renew,
                                task_1,
                                self.sock_read,
                                simple_fargs)
                        )
                        args = [gs, idc]
                        # task write
                        task_2 = loop.create_task(
                            coromask(
                                self.sock_write,
                                args,
                                simple_fargs)
                        )
                        task_2.add_done_callback(
                            functools.partial(
                                renew,
                                task_2,
                                self.sock_write,
                                simple_fargs)
                        )
                    except Exception as ex:
                        gs.abort(idc)
                        bprint("=====0000======")
                        bprint("Canceling task 1 %s" % task_1)
                        bprint("Canceling task 2 %s" % task_2)
                        bprint("=====0000======")
                        task_1.cancel()
                        task_2.cancel()
                        raise ex
            except Exception as ex:
                gs.abort()
                print("Error al levantar socket client %s" % ex)
                raise ex

                ########
                # Insert a coroutine with reader and writer tasks

            async def activate_sock():
                await socket_io()
                return "socket loaded"
            future1 = loop.create_task(activate_sock())
            print("Loop is running?", loop.is_running())
            if not loop.is_running():
                loop.run_forever()


if __name__ == "__main__":
    address = (socket.gethostbyname(socket.gethostname()), 5500)
    client = GNCSocketClient(address=address)
    client.socket_task()
