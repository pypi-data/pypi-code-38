import asyncio
import zmq
import zmq.asyncio
import socket
import cbor2
import logging


class ZMQFLPServer(object):
    def __init__(self, custom_identity=None, str_port='9001'):
        self.ctx = zmq.asyncio.Context.instance()
        # Prepare server socket with predictable identity
        if custom_identity:
            identity = custom_identity
        else:
            identity = socket.gethostbyname(socket.gethostname())
        bind_endpoint = "tcp://*:"+str(str_port)
        connect_endpoint = ('tcp://'+identity+':'+str(str_port)).encode('utf8')
        self.server = self.ctx.socket(zmq.ROUTER)
        self.server.setsockopt(zmq.ROUTER_MANDATORY, 1)
        self.server.setsockopt(zmq.IDENTITY, connect_endpoint)
        self.server.bind(bind_endpoint)
        logging.info("I: service is ready with identity " + str(connect_endpoint))
        logging.info("I: service is bound to " + str(bind_endpoint))

        self.message_table = {}

    async def receive(self):
        # Frame 0: identity of client
        # Frame 1: PING, or client control frame
        # Frame 2: request body
        try:
            request = await self.server.recv_multipart()
        except asyncio.CancelledError:
            return None, None  # Interrupted
        except Exception as e:
            logging.exception(e)
            return None, None  # Interrupted
        try:
            incoming_sequence = int(request[-2])
            if request[0] in self.message_table and self.message_table[request[0]] == incoming_sequence:
                return None, None
            else:
                self.message_table[request[0]] = incoming_sequence
                return cbor2.loads(request[-1]), request[0:-1]
                # return (await asyncio.get_running_loop().run_in_executor(None,
                #                                                          cbor2.loads,
                #                                                          request[-1]),
                #         request[0:-2])
        except Exception as e:
            logging.exception(e)
            return None, None

    async def send(self, orig_req_headers, str_resp, mpack=True):
        out_message = orig_req_headers
        if mpack:
            out_message.append(
                await asyncio.get_running_loop().run_in_executor(None,
                                                                 cbor2.dumps,
                                                                 str_resp))  # , use_bin_type=True))#.encode('utf8'))
        else:
            out_message.append(str_resp)
        await self.server.send_multipart(out_message)