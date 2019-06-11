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

from networktools.queue import send_queue, read_queue_gen

tsleep = 2


class GNCSocketServer(GNCSocketBase):

    def __init__(self, queue_n2t, queue_t2n, *args, **kwargs):
        super().__init__(queue_n2t, queue_t2n, 'server', *args, **kwargs)
        bprint("=="*30)
        rprint("(write) n2t->%s" % queue_n2t)
        rprint("(read) t2n->%s" % queue_t2n)
        bprint("=="*30)
        self.set_socket_task(self.socket_task)

    def socket_task(self):
        #print("XDX socket loop inside", flush=True)
        with GNCSocket(mode=self.mode) as gs:
            #gs = GNCSocket(mode='server')
            loop = asyncio.get_event_loop()
            self.loop = loop
            gs.set_address(self.address)
            gs.set_loop(loop)
            try:
                async def socket_io(reader, writer):
                    print("Entrando a socket -io")
                    idc = await gs.set_reader_writer(reader, writer)
                    bprint("====CLIENTES====")
                    rprint(gs.clients)
                    # First time welcome
                    welcome = json.dumps(
                        {"msg": "Welcome to socket", 'idc_server': idc})
                    print("Enviando msg welcome--%s" % welcome)
                    await gs.send_msg(welcome, idc)
                    await asyncio.sleep(0.1)
                    # task reader
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
                    except Exception as exe:
                        raise exe
                gprint("=")
                gprint("loop"+str(loop))
                rprint("Loop is runnign?<"+str(loop.is_running())+">")
                print("Creating socket server future")
                future = loop.create_task(
                    gs.create_server(socket_io, loop))
                rprint(loop.is_running())
                gprint("=")
                print("Future de server socket->")
                print(future)
                print(loop.is_running())
                if not loop.is_running():
                    loop.run_forever()
                else:
                    loop.run_until_complete(future)
            except KeyboardInterrupt:
                gs.abort()
                loop.run_until_complete(gs.wait_closed())
            except Exception as ex:
                print("Otra exception", ex)
            finally:
                print("Clossing loop on server")
                # loop.close()

        def close(self):
            self.gs.close()
