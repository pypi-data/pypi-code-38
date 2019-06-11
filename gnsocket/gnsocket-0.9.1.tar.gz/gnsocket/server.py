# Standar lib
import asyncio
import functools
from multiprocessing import Manager, Queue, Lock

# contrib modules
import ujson as json

# Own module
from .gn_socket import GNCSocket

# module tasktools
from tasktools.taskloop import coromask, renew, simple_fargs
from networktools.colorprint import gprint, bprint, rprint

from networktools.library import pattern_value, \
    fill_pattern, context_split, \
    gns_loads, gns_dumps

tsleep = 2


class GNSocketServer:

    def __init__(self, *args, **kwargs):
        self.address = kwargs.get('address', ('localhost', 6666))
        # This queue list is fixed and allow us to control
        # the scheduler system with more or less instances
        # not to send msg to every instace
        self.common_queues = kwargs.get('common_queues', {})
        self.gs = GNCSocket(mode='server')
        self.gs.set_address(self.address)
        self.rdb_status = False

    async def read_queue(self, queue):
        for i in range(queue.qsize()):
            msg_in = queue.get()
            msg = msg_in['msg']
            idc = msg_in['idc']
            await self.gs.send_msg(json.dumps(msg), idc)

    async def sock_write(self, gs, queue_t2n, idc):
        # Receive from sources and send data to clients
        rprint("New sock_write iteration")
        gs = self.gs
        queue = queue_t2n
        await asyncio.sleep(tsleep)
        try:
            print("Checking queues>qt2n? <", queue.empty(), "> on:", queue)
            if not queue.empty():
                # read control queues
                for i in range(queue.qsize()):
                    msg_in = queue.get()
                    queue.task_done()
                    msg = msg_in.get('msg')
                    idc = msg_in.get('idc')
                    bprint("()()()")
                    print("XDX Enviando mensaje: %s" % msg_in, flush=True)
                    bprint("()()()")
                    await gs.send_msg(json.dumps(msg), idc)
                # read data queues
            for ids, channel in self.common_queues.items():
                table_writer = channel.get('writer')
                # get from writer table
                cursor = await self.read_msg(table_writer)
                # gprint("#########################")
                #rprint("Ready to send by socket to user client %s" % cursor)
                # gprint("#########################")
                if cursor:
                    for c in cursor:
                        msg = c.get('msg', {})
                        bprint("Enviando a cliente user interface %s" % msg)
                        # What are we sending? --> check the test for server
                        # await gs.send_msg(json.dumps(msg), idc)
                        await gs.send_msg(json.dumps(c), idc)
        except Exception as exec:
            print("Error con modulo de escritura del socket")
            raise exec

    # socket communication terminal to engine
    async def sock_read(self, gs, queue_n2t, idc):
        # read from client and send to the manager
        # the datagrams must bring the source id: ids
        loop = asyncio.get_event_loop()
        queue = queue_n2t
        msg_from_engine = []
        await asyncio.sleep(tsleep)
        try:
            # bprint("XDX Check socket from gui", flush = True)
            # read queue is answer from msg sended
            datagram = await gs.recv_msg(idc)
            print("=============")
            print(datagram)
            msg_dict = {}
            if not datagram == '' and \
               datagram != "<END>":
                msg_dict = json.loads(datagram)
                # CHECK IF A COMMAND FOR SYSTEM
                # 'SYSTEM' in msg_dict
                bprint("====SOCK READ ON GNSOCKET SERVER ===")
                rprint(msg_dict)
                destiny = msg_dict.get('msg')[0].get('type', None)
                print("DESTINIY:::::")
                bprint(destiny)
                await asyncio.sleep(5)
                # rprint(datagram)
                # bprint(type(datagram))
                # bprint(msg_dict)
                #print("MSG Type on sock %s" % msg_dict.get('msg')[0].get('type', None))
                if destiny == 'SYSTEM':
                    # first queue sends....
                    #rprint("Sends grom network to term")
                    # gprint("=====")
                    new_dict = {
                        'dt': msg_dict,
                        'idc': idc
                    }
                    bprint("Sending data by queue to sock--->write_sock on", queue)
                    print("New dict to n2t")
                    bprint(new_dict)
                    queue.put(new_dict)
                    queue.join()
                elif destiny == 'DESTINY':
                    # print(msg_dict)
                    # print(type(msg_dict))
                    msg_dict['traces'].update({'idc_server': idc})
                    # get ids if exists or five the first ids from common_queues
                    ids = msg_dict.get('msg')[0].get(
                        'args')[0].get('ids', None)
                    #print("IDS on sock %s" % ids)
                    if ids:
                        """
                        Then the msg_dict is a correct dict with
                        the id of the source
                        """
                        #print("Sendind msg to service %s "%msg_dict)
                        # bprint(self.common_queues)
                        channel = self.common_queues.get(
                            ids, {'reader': 'interface'})
                        # print(channel)
                        table_reader = channel.get('reader')
                        # Put on the list to send to the source
                        # send msg with the traces and msg, mgs has keys ['type','command','args']
                        await self.write_msg(table_reader, msg_dict)
        except Exception as exec:
            print("Error con modulo escritura socket", exec)
            raise exec

    def socket_task(self):
        #print("XDX socket loop inside", flush=True)
        with GNCSocket(mode='server') as gs:
            #gs = GNCSocket(mode='server')
            loop = asyncio.get_event_loop()
            self.loop = loop
            gs = self.gs
            queue_list = self.queue_list
            self.active_session()
            gs.set_address(self.address)
            gs.set_loop(loop)
            try:
                async def socket_io(reader, writer):
                    print("Entrando a socket -io")
                    queue_read = queue_list[0]
                    queue_write = queue_list[1]
                    idc = await gs.set_reader_writer(reader, writer)
                    # First time welcome
                    welcome = json.dumps({"msg": "Welcome to socket"})
                    print("Enviando msg welcome--%s" % welcome)
                    await gs.send_msg(welcome, idc)
                    await asyncio.sleep(0.1)
                    if not self.rdb_status:
                        await self.init_async(loop)
                        if self.conn:
                            print("Rethinkdb connected")
                            self.rdb_status = True
                    # task reader
                    try:
                        args = [gs, queue_read, idc]
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
                        args = [gs, queue_write, idc]
                        # task write
                        task_2 = loop.create_task(
                            coromask(
                                self.sock_write,
                                args,
                                simple_fargs)
                        )
                        task_1.add_done_callback(
                            functools.partial(
                                renew,
                                task_1,
                                self.sock_write,
                                simple_fargs)
                        )
                    except Exception as exe:
                        print("Execepcion al levantar servicio", exe)
                        gs.close()
                        if not self.conn:
                            print("Clossing RDB")
                            self.conn.close()
                        raise exec
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
                    rprint("listening clients......-----=====")
                    print(self.address)
                    loop.run_forever()
                    print(future)
                else:
                    print("Running Future")
                    loop.run_until_complete(future)
            except KeyboardInterrupt:
                print("Closing socket on server")
                gs.close()
                print("Doing wait_closed")
                loop.run_until_complete(gs.wait_closed())
            except Exception as ex:
                print("Otra exception", ex)
            finally:
                print("Clossing loop on server")
                # loop.close()

        async def read_msg(self, writer, *args):
            """
            Must be implemented
            """
            return []

        async def write_msg(self, reader, *args):
            """
            Must be implemented
            """
            pass

        def active_session(self):
            pass

        async def init_async(self, loop):
            pass

        def set_reader(self, fn_reader):
            # To use when subclass
            self.read_msg = fn_reader

        def set_writer(self, fn_writer):
            # To use when subclass
            self.write_msg = fn_writer

        def close(self):
            self.gs.close()
