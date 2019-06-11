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
from gnsocket.exceptions import clean_exception

# module tasktools
from tasktools.taskloop import coromask, renew, simple_fargs
from networktools.colorprint import gprint, bprint, rprint

from networktools.library import pattern_value, \
    fill_pattern, context_split, \
    gns_loads, gns_dumps
from networktools.library import my_random_string

import ujson as json

tsleep = 2


class GNCSocketBase:

    def __init__(self, queue_n2t,
                 queue_t2n,
                 mode,
                 callback_exception=clean_exception,
                 *args,
                 **kwargs):
        self.qn2t = queue_n2t
        self.qt2n = queue_t2n
        self.address = kwargs.get('address', ('localhost', 6666))
        self.mode = mode
        self.exception = callback_exception

    async def sock_write(self, gs, idc):
        queue = self.qn2t
        await asyncio.sleep(.5)
        if idc in gs.clients:
            try:
                peername = gs.get_extra_info(idc)
                if peername:
                    for msg in read_queue_gen(queue):
                        msg_send = json.dumps(msg)
                        idc_server = msg.get('idc_server')
                        await gs.send_msg(msg_send, idc)
                else:
                    print("Error en conexión socket sock_write")
                    raise Exception("Peername fail")
            except Exception as ex:
                print("Error con modulo de escritura del socket IDC %s" % idc)
                gs.set_status(False)
                del gs.clients[idc]
                if self.exception:
                    self.exception(ex, gs, idc)
        else:
            await asyncio.sleep(20)
    # socket communication terminal to engine

    async def sock_read(self, gs, idc):
        queue = self.qt2n
        msg_from_engine = []
        await asyncio.sleep(.5)
        if idc in gs.clients:
            try:
                peername = gs.get_extra_info(idc)
                datagram = await gs.recv_msg(idc)
                bprint("Reading socket msg")
                rprint(datagram)
                if datagram not in {'', "<END>", 'null', None}:
                    msg_dict = json.loads(datagram)
                    rprint("Msg received from client-> %s" % msg_dict)
                    msg = {'dt': msg_dict, 'idc': idc}
                    queue.put(msg)
            except Exception as ex:
                print("Some error %s en sock_read" % ex)
                gs.set_status(False)
                del gs.clients[idc]
                if self.exception:
                    self.exception(ex, gs, idc)
        else:
            await asyncio.sleep(20)

    def set_socket_task(self, callback_socket_task):
        self.socket_task = callback_socket_task
