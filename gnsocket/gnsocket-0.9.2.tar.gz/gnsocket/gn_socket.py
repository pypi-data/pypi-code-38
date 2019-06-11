# -*- coding: utf-8 -*-

# Echo server program
import os
import socket
import asyncio
import errno
import math
import re
import logging
import ssl
from pathlib import Path

# These values are constant
try:
    from conf.socket_conf import AF_TYPE, SOCK_TYPE
    from conf.socket_conf import HEADER
    from conf.socket_conf import ENDER
    from conf.socket_conf import sock
    from conf.socket_conf import gnc_path
    from conf.socket_conf import t_out
    from conf.socket_conf import buffsize
    from conf.socket_conf import uin
    from conf.socket_conf import char_code
    from conf.socket_conf import n_listen
    from conf.socket_conf import address

except Exception:
    from .conf.socket_conf import AF_TYPE, SOCK_TYPE
    from .conf.socket_conf import HEADER
    from .conf.socket_conf import ENDER
    from .conf.socket_conf import sock
    from .conf.socket_conf import gnc_path
    from .conf.socket_conf import t_out
    from .conf.socket_conf import buffsize
    from .conf.socket_conf import uin
    from .conf.socket_conf import char_code
    from .conf.socket_conf import n_listen
    from .conf.socket_conf import address

from networktools.library import (pattern_value,
                                  fill_pattern,
                                  context_split,
                                  gns_loads,
                                  gns_dumps,
                                  my_random_string,
                                  complete_nro,
                                  hextring,
                                  hextring2int)

from networktools.colorprint import gprint, bprint, rprint


# Asyncio guide:
# http://www.snarky.ca/how-the-heck-does-async-await-work-in-python-3-5

# More ref about socket:
# http://stackoverflow.com/questions/27014955/socket-connect-vs-bind

# example:

# Best example: https://gist.github.com/jamilatta/7603968

# from scheduler import ReadWait, WriteWait

import uuid

import chardet

from networktools.time import timestamp


def logfile(module):
    return './logs/gnsocket_%s_%s.log' % (module, str(timestamp())[:-7])


class GNCSocket:
    """
    Socket class for GNC
    Create or connect to an UNIX/TCP socket
    Methods:
    * connect
    * send_msg
    * recv_msg
    * server
    * client
    """

    def __init__(self, mode='server', address=address, **kwargs):
        self.bs = buffsize
        self.gnc_path = gnc_path
        self.mode = mode
        # default timeout
        self.timeout = kwargs.get('timeout', t_out)
        self.module = kwargs.get('module', 'test')
        self.ssl = kwargs.get('ssl', False)
        # IF SSL ACTIVE
        if self.ssl:
            self.set_ssl(**kwargs)
        else:
            self.context = None
        ####
        self.status = False
        print(self.status)
        # self.set_logger()
        if mode == 'server':
            self.set_server(AF_TYPE, address)
            self.server = None
        if mode == 'client':
            self.set_client(AF_TYPE, address)
        # BIND: connect a path with socket
        # Print type
        # print(sock.SocketType)
        # self.sock.bind(path_gnc_socket)
        # Set timeout
        self.conss = []
        self.addrs = []
        self.backlog = n_listen
        # MSG Format
        # Defined:
        # LEN_HEAD MSG LCHAR(hex) LEN MSG END
        # Send format
        self.msg_struct = b"IDX hex(PAGE)/hex(TOT_PAGES) MSG hex(LEN) MSG END"
        self.msg_template = "{idx} {page}/{tot_pages} MSG {length} MSG END"
        self.msg_spaces = [x.start()
                           for x in re.finditer(b' ', self.msg_struct)]
        # IDX hex(PAGE)/hex(TOT_PAGES) MSG hex(LEN) MSG END
        # How to generate:
        # msg -> bytes
        # len(msg_bytes)
        # # envios
        # self.msg_limit = msg_limit
        # self.msg_limit_hex = str(hex(self.msg_limit)).split('x')[1]
        # self.nchar = len(self.msg_limit_hex)
        # Limit_msg = 512 (default), n=len(str(512))
        # To hex: 0x200
        # Split x
        # Get value and complete => LCHAR (en hex)
        self.header = HEADER
        self.ender = ENDER
        self.uin = uin
        self.idx = []
        self.conns = []
        self.addrs = []
        self.msg_r = ''
        # asyncio coroutines
        self.alert = ""
        self.loop = ''
        self.mq = {}
        self.addresss = address
        # message queues
        self.clients = {}
        self.idc = []
        self.server = object
        self.queue_socket_status = None

    def set_queue_socket_status(self, queue):
        self.queue_socket_status = queue

    def set_ssl(self, **kwargs):
        purpose_key = kwargs.get('ssl_protocol', 'tls')
        self.protocols = {
            'tls': ssl.PROTOCOL_SSLv23,
        }
        self.protocol = self.protocols.get(purpose_key, ssl.PROTOCOL_SSLv23)
        self.set_certs = kwargs.get('set_certificates',
                                    {'cafile': None,
                                     'capath': None,
                                     'cadata': None,
                                     'crtkey': None})
        data_ssl = {}
        data_ssl.update(self.set_certs)
        self.ssl_context(self.protocol, data_ssl)

    def ssl_context(self, protocol, data_ssl):
        print("Set SSL connection with protocol %s" % protocol)
        self.context = ssl.SSLContext(protocol)
        crt = data_ssl.get('cafile')
        key = data_ssl.get('crtkey')
        if self.mode == 'server':
            self.context.load_cert_chain(crt, key)
        elif self.mode == 'client':
            path = data_ssl.get('cadata')
            data = data_ssl.get('capath')
            self.context.load_verify_locations(crt, path, data)
        print("SSL Settings end")

    def send_msg_sock_status(self, value):
        msg = {'command': 'socket_bar',
               'status': value}
        if self.queue_socket_status:
            self.queue_socket_status.put(msg)
            self.queue_socket_status.join()

    def set_logger(self):
        # log file for this station
        self.filelog = logfile(self.module)
        self.logpath = Path('./logs')
        if not self.logpath.exists():
            os.makedirs(str(self.logpath))

        # create log instance
        logger = logging.getLogger('%s_gnss' % self.module)
        handler = logging.FileHandler(self.filelog, mode='w')
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s  %(process)d %(pathname)s \
            %(filename)s %(module)s %(funcName)s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        self.logger.info("Se inicializa nuevo GNSOCKET")

    def set_server(self, AF_TYPE, address):
        if AF_TYPE == socket.AF_UNIX:
            self.address = self.gnc_path
            if os.path.exists(self.gnc_path):
                os.remove(self.gnc_path)
        elif AF_TYPE == socket.AF_INET:
            self.address = address
        # self.logger.info("Se crea un socket server")

    def set_client(self, AF_TYPE, address):
        if AF_TYPE == socket.AF_UNIX:
            self.address = self.gnc_path
        elif AF_TYPE == socket.AF_INET:
            self.address = address
        # self.logger.info("Se crea un socket client")

    def set_status(self, value):
        if value in [True, False]:
            self.status = value
        else:
            print("Status don't change")
        # self.logger.info("Se crea modifica status a %s" %value)

    def switch_status(self):
        self.status = not self.status
        # self.logger.info("Se crea modifica status a %s" %self.status)

    def get_status(self):
        return self.status

    def set_loop(self, loop):
        print(format(loop))
        self.loop = loop

    def get_writer(self, idc):
        return self.clients[idc]['writer']

    def get_reader(self, idc):
        return self.clients[idc]['reader']

    def generate_msg(self, msg):
        # self.msg_struct = b"IDX hex(PAGE)/hex(TOT_PAGES) MSG hex(LEN) MSG END"
        # self.msg_tempalte = b"{header} {page}/{tot_pages} MSG {length} MSG END"
        assert isinstance(msg, str), "The msg must be string"
        b_msg = msg.encode(char_code)
        T_LEN = len(b_msg)
        # Cantidad de caracteres en hexadecimal
        hex_T_LEN = hextring(T_LEN)
        # Se obtiene el largo de caracteres como
        # cota superior de largo de mensaje
        # A utilizar en paginacion
        # largo del valor
        new_n = len(hex_T_LEN)
        # n_char es lo mismo
        self.n_char = new_n
        # obtener el largo base del mensaje
        self.base_len = len(self.header) + len(self.ender) + \
            len(self.msg_spaces) + self.uin + 3 * self.n_char + 1
        # n_char is the amount of chars for numvers
        # tha last  +1 is for the space after IDX
        # Largo de pedazo de mensaje a enviar por partes
        self.len_msg = self.bs - self.base_len
        assert self.len_msg >= 1, "Debes definir un buffsize de mayor tamaño"
        assert new_n + 1 < self.len_msg, "No es posible enviar mensaje"
        # Cantidad maxima de mensajes a enviar
        n_msgs = math.ceil(T_LEN / self.len_msg)
        # transformar a hex y sacar strign
        hex_n_msgs = hextring(n_msgs)
        # Cantidad de paginas
        self.N_n_msgs = len(str(hex_n_msgs))
        # hex_nmsgs = str(hex(n_msgs)).split('x')[1]
        ender = self.ender.encode(char_code)
        # Se construye: hex(PAGE)/hex(TOT_PAGES) MSG hex(LEN) MSG END
        NON = "".encode(char_code)
        head_template = "{header} {page}/{tot_pages} {length} "
        msg_ender = " END"
        if n_msgs > 1:
            for i in range(n_msgs):
                # Construir header:
                # Conocer parte de msg a enviar
                # Conocer largo de msg_i
                # Cantidad carácteres largo
                step = i * self.len_msg
                this_page = hextring(i + 1)
                msg_i = b_msg[step:step + self.len_msg]
                msg_l = len(msg_i)
                # +2 erased because quoted don't go
                msg_len = msg_l + len(ender)
                # print("MSG to send -> Encoded by" , the_encoding)
                componentes = {
                    'header': self.header,
                    'page': complete_nro(this_page, n=new_n),
                    'tot_pages': complete_nro(hex_n_msgs, n=new_n),
                    'length': complete_nro(hextring(msg_len), n=new_n)
                }
                msg_header = head_template.format(**componentes)
                this_msg = NON.join([msg_header.encode(char_code),
                                     msg_i,
                                     msg_ender.encode(char_code)])
                #bprint("Generated msg Encoded by")
                # rprint(this_msg)
                yield this_msg

        elif n_msgs == 1:
            this_page = hextring(1)
            msg_len = (T_LEN + len(ender))
            hex_msg_len = complete_nro(hextring(msg_len), n=new_n)
            componentes = {
                'header': self.header,
                'page': complete_nro(this_page, n=new_n),
                'tot_pages': complete_nro(hextring(1), n=new_n),
                'length': complete_nro(hextring(msg_len), n=new_n)
            }
            msg_header = head_template.format(**componentes)
            this_msg = NON.join([msg_header.encode(char_code),
                                 b_msg,
                                 msg_ender.encode(char_code)])
            #print("Generated msg Encoded by" , the_encoding)
            yield this_msg

    def gen_idx(self):
        IDX = my_random_string(self.uin)
        t = True
        while t:
            if IDX not in self.idx:
                self.idx.append(IDX)
                t = False
            else:
                IDX = my_random_string(self.uin)
        return IDX

    async def send_msg(self, msg, id_client):
        writer = self.clients.get(id_client).get('writer')
        # tot = self.N_n_msgs
        try:
            if writer.transport.is_closing():
                # self.logger.error("La conexión se cerró %s" % self.status)
                raise Exception("Conexión perdida")
            # assert tot == len(msg), "Hay un cruce de mensajes"
            await self.send_text(msg, writer)
            await self.send_text('<END>', writer)
        except socket.error as exec:
            # self.logger.error("Hubo una excepción, error en socket %s" % self.status)
            raise exec
        except Exception as exec:
            self.set_status(False)
            # self.logger.error("Hubo una excepción %s" % self.status)
            print(exec)
            raise exec
        except asyncio.CancelledError as exec:
            # self.logger.error("Hubo una excepción,
            # error de cancelación con modulo asyncio %s" % self.status)
            raise exec
    # Coroutine

    async def send_text(self, msg, writer):
        IDX = self.gen_idx().encode(char_code)
        for b_msg in self.generate_msg(msg):
            # print(b_msg)
            # Here the splited messages
            # First value is header length
            # Catch them
            # 1+1+self.uin
            # Find first space to get index from header len value
            to_send = b"".join([IDX, b" ", b_msg])
            # print("Contexted:::>",q)
            # yield WriteWait(conn)
            if writer.get_extra_info('peername'):
                writer.write(to_send)
                # Transport.write(data)
                await writer.drain()
            else:
                writer.write_eof()
                await writer.close()

    def get_extra_info(self, idc):
        writer = self.clients.get(idc).get('writer')
        return writer.get_extra_info('peername')

    def send_eof(self, id_client):
        writer = self.clients.get(id_client).get('writer')
        writer.write_eof()

    def abort(self, id_client):
        writer = self.clients.get(id_client).get('writer')
        writer.abort()

    def at_eof(self, id_client):
        reader = self.clients.get(id_client).get('reader')
        return reader.at_eof()

    def feed_eof(self, id_client):
        reader = self.clients.get(id_client).get('reader')
        reader.feed_eof()

    async def recv_msg(self, id_client):
        reader = self.clients[id_client]['reader']
        writer = self.clients[id_client]['writer']
        # addr = self.addr
        bs_0 = 1
        count = 0
        b_header = b''
        idx_recv = ''
        t = True
        msg_tot = b''
        mlist = []
        n_msgs_idx = 0
        try:
            # moment 1 -> get hueader
            if writer.transport.is_closing():
                # self.logger.error("La conexión se cerró %s" % writer)
                raise Exception("Conexión perdida")
            idx_recv = ''
            page = [0, 0]
            while t:
                peername = writer.get_extra_info('peername')
                while count < 4 and peername:
                    if not reader.at_eof():
                        # moment 2 -> get content message, check if there are more
                        try:
                            char_recv = await reader.read(n=bs_0)
                        except Exception as ex:
                            raise Exception("Conexión perdida -> %s" % ex)
                    else:
                        ex = reader.exception()
                        raise Exception("Conexión perdida -> EOF")
                    b_header += char_recv
                    if char_recv == b" ":
                        count += 1
                    peername = writer.get_extra_info('peername')
                    if not peername:
                        ex = reader.exception()
                        raise Exception(
                            "Conexión perdida -> Not Peername" % ex)
                header = b_header.decode(char_code)
                b_header = b''
                spaces = [x.start() for x in re.finditer(' ', header)]
                # bprint("=======Spaces=======")
                # rprint(spaces)
                sp_1 = spaces[0]
                sp_2 = spaces[1]
                sp_3 = spaces[2]
                s_page = header[sp_2 + 1:sp_3].split("/")
                # gprint("HEADER")
                # rprint(header)
                # bprint("S PAGE ON SOCKET")
                # rprint(s_page)
                a = page[0]
                b = page[1]
                page = list(map(hextring2int, s_page))
                sp_4 = spaces[3]
                check_header = header[sp_1 + 1:sp_2]
                # bprint("Check header spaces_0 -> spaces_1")
                # rprint(check_header)
                assert self.header == header[sp_1 + 1:
                                             sp_2], "No es un encabezado correcto"
                this_idx_recv = header[:sp_1]
                # bprint("IDX received")
                # rprint(this_idx_recv)
                # rprint("Counter......")
                # bprint(n_msgs_idx)
                if idx_recv == '':
                    idx_recv = this_idx_recv
                    n_msgs_idx = 1
                else:
                    n_msgs_idx += 1
                # bprint("IDX>")
                # rprint(n_msgs_idx)
                # bprint(page)
                assert n_msgs_idx == page[
                    0], "Error en mensaje, no coincide #idx con pagina " + str(
                        page[0])
                lmsg = header[sp_3 + 1:sp_4]
                #bprint("HEXLength mgs")
                # rprint(lmsg)
                #bprint("Length mgs")
                # rprint(hextring2int(lmsg))
                bs_1 = hextring2int(lmsg)+1
                # gprint("BS1")
                # bprint(bs_1)
                if not reader.at_eof():
                    try:
                        # moment 3 -> get next slice of msg
                        b_MSG = b''
                        n = 0
                        while n < bs_1:
                            if writer.get_extra_info('peername'):
                                if not reader.at_eof():
                                    # moment 2 -> get content message, check if there are more
                                    try:
                                        bm = await reader.read(n=1)
                                    except Exception as ex:
                                        raise Exception(
                                            "Error en conexión %s" % ex)
                                b_MSG += bm
                                # rprint("MSG--->")
                                # bprint(b_MSG)
                                # rprint(bs_1)
                                # gprint(n)
                                n += 1
                    except Exception as ex:
                        # self.logger.error("La conexión se cerró debido con reader %s," % reader)
                        raise Exception("Conexión perdida -> %s" % ex)
                l_ender = len(self.ender.encode(char_code))
                # PROBLEM WITH DECODE BEFORE JOIN
                # print("===========")
                # print(b_MSG)
                # bprint(len(b_MSG))
                nlast = b_MSG.rfind(b" ")
                pre_msg = b_MSG[:nlast]
                #print("Pre msg", pre_msg)
                #print(pre_msg[0:1], pre_msg[-1::])
                # if pre_msg[0:1] == h:
                #    qmsg = pre_msg[1::]
                # if pre_msg[-1::]==h:
                #    wmsg = qmsg[:-1]
                #print("Pre context split")
                count = 0
                #print("Msg recibido en socket read_socket %s" % pre_msg)
                #bprint("page_0 == page_1")
                #rprint(page[0] == page[1])
                if pre_msg == b"<END>" or page[0] == page[1]:
                    # rprint("==========================")
                    #bprint("Fin de mensaje")
                    # rprint("==========================")
                    t = False
                    mlist.append(pre_msg)
                    n_msgs_idx = 0
                    #print("Cerrando", mlist)
                    break
                else:
                    mlist.append(pre_msg)
                    #print("Added msg ", mlist)
        except Exception as exec:
            # self.logger.error("La conexión se cerró debido con %s," % exec)
            print("Read error")
            print(exec)
            raise exec
        except asyncio.CancelledError as exec:
            # self.logger.error("La conexión se cerró debido con CancelledError")
            raise exec
        except socket.error as exec:
            # self.logger.error("La conexión se cerró debido a SocketError")
            raise exec

        #print("Procesando final")
        msg_tot = b"".join(mlist)
        #print("MSG JOINED", msg_tot)
        MSG_TOT = msg_tot.decode(char_code)
        MT = MSG_TOT.strip()
        MT = MSG_TOT.rstrip()
        #print("Fin del mensaje", MSG_TOT)
        self.msg_r = MSG_TOT
        return MSG_TOT

    def get_path(self):
        return self.gnc_path

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def set_path(self, new_gnc_path):
        if os.path.exists(new_gnc_path):
            os.remove(new_gnc_path)
        self.gnc_path = new_gnc_path

    # callback for create server:

    def set_idc(self):
        """
        Defines a new id for relation process-collect_task, check if exists
        """
        uin = 4
        idc = my_random_string(uin)
        while True:
            if idc not in self.idc:
                self.idc.append(idc)
                break
            else:
                idc = my_random_string(uin)
        return idc

    async def set_reader_writer(self, reader, writer):
        idc = self.set_idc()
        # self.log_info_client(writer)
        self.clients.update(
            {idc: {
                'reader': reader,
                'writer': writer
            }
            }
        )
        return idc

    def log_info_client(self, writer):
        names = ['peername', 'socket', 'sockname']
        for name in names:
            info = writer.get_extra_info(name)
            # self.loggger.info("La info correspondiente a %s es %s" %(name, info))

    def off_blocking(self):
        if self.mode == 'server':
            [sock.setblocking(False) for sock in self.server.sockets]
        elif self.mode == 'client':
            pass

    def on_blocking(self):
        if self.mode == 'server':
            [sock.setblocking(True) for sock in self.server.sockets]
        elif self.mode == 'client':
            pass

    def settimeout(self, timeout=5):
        [sock.settimeout(timeout) for sock in self.server.sockets]

    async def connect(self):
        """
        Connect client to socket
        """
        while not self.status:
            try:
                result = await self.loop.sock_connect(
                    self.sock, self.address)
                self.alert = "Conectado a socket-base"
                self.status = True
                print("Resultado de conectar socket")
                print(result)
                # self.logger.info("Conexión a %s realizada" % self.address)
                break
            except socket.timeout as timeout:
                # self.on_blocking()
                # self.logger.error(
                #     "Error en conexión con %s, error: %s" % (self.address, timeout))
                print("Error de socket a GSOF \
                en conexión %s, %s" % (self.address, timeout))
                self.status = False
                await asyncio.sleep(.5)
                await self.connect()  # go to begin -|^
            except socket.error as e:
                self.status = False
                # self.on_blocking()
                if e.errno == errno.ECONNREFUSED:
                    pass
                    # self.logger.error(e)
                else:
                    pass
                    # self.logger.error(e)

    def clean_socket(self, host, port):
        comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("ex socket->ComSocket:::", comSocket)
        print(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        print(socket.SOL_SOCKET, socket.SO_REUSEPORT)
        print("Cleaning address", (host, port))
        comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # comSocket.shutdown(socket.SHUT_RDWR)

    async def create_server(self, callback_io, loop):
        # SI ES UNIX SOCKET
        # includes  bind
        # https://github.com/python/asyncio/blob/fff05d480760703adbc3e2d4cb3dbcfbff803c29/asyncio/unix_events.py
        bprint("loop runin before create server")
        print(loop.is_running())
        mode = self.mode
        context = self.context
        print("Creando server---_>")
        print(loop, mode, context, AF_TYPE)
        self.server = None
        try:
            if mode == 'server':
                if AF_TYPE == socket.AF_UNIX:
                    print("Se crea Socket Server Unix")
                    # ref https://docs.python.org/3/library/asyncio-eventloop.html
                    future_server = asyncio.start_unix_server(callback_io,
                                                              loop=loop,
                                                              path=self.get_path(),
                                                              limit=self.backlog,
                                                              ssl=context)
                    self.server = await asyncio.wait_for(future_server, timeout=self.timeout)
                elif AF_TYPE in {socket.AF_INET, socket.AF_INET6}:
                    host = self.address[0]
                    port = self.address[1]
                    print("Se crea Socket Server TCPx")
                    print("Cleaning address")
                    self.clean_socket(host, port)
                    print("Closing cleaning address")
                    gprint("New server listening......")
                    rprint(host)
                    rprint(port)
                    future_server = asyncio.start_server(
                        callback_io,
                        loop=loop,
                        host=host,
                        port=port,
                        family=AF_TYPE,
                        backlog=self.backlog,
                        ssl=context)
                    bprint("Future coro to run server:::")
                    rprint(future_server)
                    self.server = await asyncio.wait_for(future_server, timeout=self.timeout)
                    rprint("(create_server works!)El server es")
                    print(loop)
                    print(self.server, type(self.server))
            else:
                print("Asigna primero mode=server")
        except Exception as ex:
            print("Excepcion en create_server <::::", ex, "::::>")
        except asyncio.TimeoutError as te:
            print("Timeout error", te)
            raise te
        self.status = 'OFF'
        return self.server

    async def create_client(self):
        mode = self.mode
        loop = self.loop
        self.send_msg_sock_status(20)
        try:
            if mode == 'client':
                if AF_TYPE == socket.AF_UNIX:
                    # ref https://docs.python.org/3/library/asyncio-eventloop.html
                    future_unix_client = asyncio.open_unix_connection(
                        loop=loop, path=self.get_path(), ssl=self.context)
                    (reader, writer) = await asyncio.wait_for(future_unix_client, timeout=self.timeout)
                    self.send_msg_sock_status(40)
                elif AF_TYPE == socket.AF_INET or AF_TYPE == socket.AF_INET6:
                    host = self.address[0]
                    port = self.address[1]
                    print("La direccion es %s con tipo: %s " % (self.address,
                                                                AF_TYPE))
                    print(loop)
                    future_client = asyncio.open_connection(
                        loop=loop,
                        host=host,
                        port=port,
                        ssl=self.context)
                    (reader, writer) = await asyncio.wait_for(future_client, timeout=self.timeout)
                    self.send_msg_sock_status(40)
        except Exception as ex:
            print("Excepcion en", ex)
            self.send_msg_sock_status(-1)
            raise ex
        except asyncio.TimeoutError as te:
            print("Timeout error")
            self.send_msg_sock_status(-1)
            raise te
        self.alert = "Conectado a socket-base"
        self.status = 'ON'
        print(self.alert)
        idc = await self.set_reader_writer(reader, writer)
        self.send_msg_sock_status(50)
        return idc

    def set_backlog(self, new_backlog):
        # ?
        assert isinstance(new_backlog,
                          int), "El nuevo backlog no es un valor válido"
        self.backlog = new_backlog

    async def accept(self):
        conn, addr = await self.loop.sock_accept(self.server.sockets[0])
        self.conns.append(conn)
        self.addrs.append(addr)
        self.conn = conn
        self.addr = addr
        self.status = 'ON'
        return conn, addr

    def list_clients(self):
        for i in range(len(self.conss)):
            print(str(self.addrs[i]) + ":" + str(self.conns[i]))

    def close(self):
        self.status = 'OFF'
        [client.get('writer').close() for ids, client in self.clients.items()]
        self.clean_socket(*self.address)
        if self.mode == 'server':
            if self.server:
                self.server.close()

    def clean_client(self, idc):
        if idc in self.clients:
            client = self.clients.get(idc)
            client.get('writer').close()
            del self.clients[idc]

    async def wait_closed(self):
        for ids, client in self.clients.items():
            await client.get('writer').wait_closed()
        if self.mode == 'server' and self.server:
            await self.server.wait_closed()

    async def server(self):
        await self.create_server()

    async def client(self):
        await self.create_client()
        # Connect to path

    def get_name(self):
        return self.gnc_path

    def __enter__(self):
        print("Starting GNC Socket (enter)")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        bprint("="*20)
        print("Enviando EOF al otro lado")
        print("Clossing succesful, Socket exit->",
              exception_type, exception_value, traceback)
        print("Socket exit -> traceback", traceback)
        print("Closing GNC Socket")
        # self.close()
        print("Socket closed")
        print(self.loop)
        print("Loop status |^")
        # self.loop.run_until_complete(self.wait_closed())
        bprint("="*20)

        # UNIX socket need a path

        # AF_UNIX is a constant, represent the address and protocol family
        # Feom socket man page
        # http://man7.org/linux/man-pages/man7/unix.7.html
        # is used to communicate betwen processes on SAME machine efficiently
        # So, the valid socket type: SOCK_STREAM

        # SOCK_STREAM
        # SOCK_STREAM     Provides sequenced, reliable, two-way, connection-
        #                 byte streams.  An out-of-band data transmission
        #                 mechanism may be supported.

        # Sockets of type SOCK_STREAM are full-duplex byte streams.  They do
        # preserve record boundaries.  A stream socket must be in a
        # state before any data may be sent or received on it.  A
        # to another socket is created with a connect(2) call.  Once
        # , data may be transferred using read(2) and write(2) calls
        # some variant of the send(2) and recv(2) calls.  When a session has
        # completed a close(2) may be performed.  Out-of-band data may
        # be transmitted as described in send(2) and received as described
        # recv(2).

        # communications protocols which implement a SOCK_STREAM ensure
        # data is not lost or duplicated.  If a piece of data for which
        # peer protocol has buffer space cannot be successfully transmitted
        # a reasonable length of time, then the connection is considered
        # be dead.  When SO_KEEPALIVE is enabled on the socket the protocol
        # in a protocol-specific manner if the other end is still alive.
        # SIGPIPE signal is raised if a process sends or receives on a broken
        # ; this causes naive processes, which do not handle the signal,
        # exit.  SOCK_SEQPACKET sockets employ the same system calls as
        # _STREAM sockets.  The only difference is that read(2) calls will
        # only the amount of data requested, and any data remaining in
        # arriving packet will be discarded.  Also all message boundaries
        # incoming datagrams are preserved.

        # From man socket: http://man7.org/linux/man-pages/man2/socket.2.html

        # PEP 383 https://www.python.org/dev/peps/pep-0383/ string path names

    # async def gnc_socket():
    # Listen on socket

    # While

    # Read from server

    # Read from socket

    # Send to socket

    # loop = asyncio.get_event_loop()

    # loop.run_until_complete(gnc_socket)

    # loop.close()
