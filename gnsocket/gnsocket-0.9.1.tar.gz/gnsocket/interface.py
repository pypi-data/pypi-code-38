import asyncio
from tasktools.taskloop import coromask, renew, simple_fargs


class AbstractSocketInterface:
    def __init__(self, gsocket, *args, **kwargs):
        self.gs = gsocket
        self.queue_g2s = kwargs.get('queue_g2s')
        self.queue_s2g = kwargs.get('queue_s2g')

    async def sock_write(self, *args, **kwargs):
        pass

    async def sock_read(self, *args, **kwargs):
        pass


class SocketInterface:
    def __init__(self, gsocket, *args, **kwargs):
        self.gs = gsocket
        self.queue_g2s = kwargs.get('queue_g2s')
        self.queue_s2g = kwargs.get('queue_s2g')

    async def sock_write(self, idc):
        gs = self.gs
        queue = self.queue_g2s
        await asyncio.sleep(tsleep)
        try:
            print("Check queue from GUI is empty")
            print(queue)
            print(queue.empty())
            if not queue.empty():
                for i in range(queue.qsize()):
                    msg_in = queue.get()
                    bprint("Recibido desde gui : %s" % msg_in)
                    await gs.send_msg(gns_dumps(msg_in), idc)
            else:
                pass
        except Exception as exec:
            print("Error con modulo de escritura del socket")
            raise exec
    # socket communication terminal to engine

    async def sock_read(self, idc):
        gs = self.gs
        queue = self.queue_s2g
        msg_from_engine = []
        await asyncio.sleep(tsleep)
        try:
            print("Check if there are messages from source")
            # read queue is answer from msg sended
            datagram = await gs.recv_msg(idc)
            bprint("Recibido desde socket server %s " % datagram)
            if not datagram == '' and \
               datagram != "<END>":
                queue.put(gns_loads(datagram))
        except Exception as exec:
            raise exec

    def socket_task(queue_list):
        # client socket
        print("Socket tasks: (writer, reader)")
        loop = asyncio.get_event_loop()
        gs.set_loop(loop)

        async def socket_io(queue_list):
            queue_read = queue_list[0]
            queue_write = queue_list[1]
            idc = await gs.create_client()
            # First time welcome
            #welcome={'command':'greetings', 'args':["Welcome to socket"]}
            # rprint(welcome)
            # await gs.send_msg(welcome)
            # await gs.send_msg("<END>")
            # task reader
            try:
                args = [queue_read, idc]
                task_1 = loop.create_task(
                    coromask(
                        sock_read,
                        args,
                        simple_fargs)
                )
                task_1.add_done_callback(
                    functools.partial(
                        renew,
                        task,
                        sock_read,
                        simple_fargs)
                )
                args = [queue_write, idc]
                # task write
                task_2 = loop.create_task(
                    coromask(
                        sock_write,
                        args,
                        simple_fargs)
                )
                task_2.add_done_callback(
                    functools.partial(
                        renew,
                        task,
                        sock_write,
                        simple_fargs)
                )
            except Exception as exec:
                raise exec

        ########
        # Insert a coroutine with reader and writer tasks

        async def activate_sock(queue_list):
            await socket_io(queue_list)
            return "socket loaded"

        future1 = loop.create_task(activate_sock(queue_list))

        print("Loop is running?", loop.is_running())
        if not loop.is_running():
            loop.run_forever()
