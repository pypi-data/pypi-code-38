import asyncio
from gnsocket.gn_socket import GNCSocket
from gnsocket.conf.socket_conf import TEST_TEXT
from tasktools.taskloop import coromask, renew, simple_fargs
import functools
from termcolor import colored, cprint

def gprint(text):
    msg = colored(text, 'green', attrs=['reverse', 'blink'])
    print(msg)

def bprint(text):
    msg = colored(text, 'blue', attrs=['reverse', 'blink'])
    print(msg)

def rprint(text):
    msg = colored(text, 'red', attrs=['reverse', 'blink'])
    print(msg)

if __name__ == "__main__":
    mode = 'server'
    gs = GNCSocket(mode=mode)
    print(gs.gnc_path)
    msg = TEST_TEXT

    # Testing message generator
    print("Status " + gs.status)
    for m in gs.generate_msg(msg):
        print(m.decode('utf-8'))
    # gs.send_msg(msg)
    # gs.send_msg(msg)
    # print(gs.conn)
    # Testing communicate
    print(gs)
    print("Entrando a loop")
    loop = asyncio.get_event_loop()
    gs.set_loop(loop)
    tsleep=1# 1 second sleep by some coroutines
    # Create coroutines
    async def sock_read(queue):
        bprint("Sock read")
        try:
            datagram = await gs.recv_msg()
            bprint("msg recibido")
            if not datagram == '' and \
               datagram != "<END>":
                await queue.put(datagram)
            await asyncio.sleep(tsleep)
            # print(msg_tot)
        except Exception as exec:
            gs.set_status('OFF')
            raise exec

    async def sock_write(queue):
        rprint("Sock write")
        print("Connection %s " % format(gs.writer.transport.is_closing()))
        #read async queue
        try:
            if not queue.empty():
                for q in range(queue.qsize()):
                    msg=await queue.get()
                    await gs.send_msg(msg)
                await gs.send_msg("<END>")
                rprint("Msg enviado")
            await asyncio.sleep(tsleep)
        except Exception as exec:
            gs.set_status('OFF')
            raise exec

    async def socket_io(reader, writer):
        queue=asyncio.Queue()
        await gs.set_reader_writer(reader, writer)
        #First time welcome
        welcome="Welcome to socket"
        rprint(welcome)
        await gs.send_msg(welcome)
        await gs.send_msg("<END>")
        #task reader
        try:
            args=[queue]
            task=loop.create_task(
                coromask(
                    sock_read,
                    args,
                    simple_fargs)
            )
            task.add_done_callback(
                functools.partial(
                    renew,
                    task,
                    sock_read,
                    simple_fargs)
            )
            #task write
            task=loop.create_task(
                coromask(
                    sock_write,
                    args,
                    simple_fargs)
            )
            task.add_done_callback(
                functools.partial(
                    renew,
                    task,
                    sock_write,
                    simple_fargs)
            )
        except Exception as exec:
            raise exec

    try:
        future=loop.create_task(gs.create_server(socket_io))
        loop.run_forever()
    except:
        future.exception()
        raise
    
    loop.close()
    gs.close()
