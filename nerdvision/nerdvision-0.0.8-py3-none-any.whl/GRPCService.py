import base64
import logging

import grpc
import nerdvision_pb2
import nerdvision_pb2_grpc

from nerdvision import settings

our_logger = logging.getLogger("nerdvision")


class GRPCService(object):
    def __init__(self, remote_id):
        self.channel = None
        self.api_key = settings.get_setting("api_key")
        self.remote_id = remote_id
        self.service_url = settings.get_grpc_host()
        our_logger.info("Configured GRPC with remote_id: %s; api_key: %s; service url: %s", self.remote_id, self.api_key,
                        self.service_url)

    def connect(self, call_back):
        self.channel = grpc.secure_channel(self.service_url, grpc.ssl_channel_credentials())

        with self.channel as channel:
            breakpoints_stub = nerdvision_pb2_grpc.NerdVisionBreakpointsStub(channel)

            connection = nerdvision_pb2.BreakpointConnection()

            encode = base64.b64encode((self.remote_id + ':' + self.api_key).encode("utf-8"))

            stream_breakpoints = breakpoints_stub.streamBreakpoints(connection, metadata=[
                ('authorization', "Basic%20" + encode.decode('utf-8'))])

            for response in stream_breakpoints:
                call_back(response)

    def stop(self):
        self.channel.close()
