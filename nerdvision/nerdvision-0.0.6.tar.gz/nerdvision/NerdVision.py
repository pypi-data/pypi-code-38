from threading import Thread

from grpc import RpcError

import nerdvision
from nerdvision.BreakpointService import BreakpointService
from nerdvision.ClientRegistration import ClientRegistration
from nerdvision.GRPCService import GRPCService


class NerdVision(object):
    def __init__(self):
        self.logger = nerdvision.configure_logger()
        self.logger.info("Starting NerdVision %s", nerdvision.__version__)
        self.registration = ClientRegistration()
        self.session_id = self.registration.run_and_get_session_id()
        self.grpc_service = GRPCService(self.session_id)
        self.breakpoint_service = BreakpointService(self.session_id)
        self.thread = Thread(target=self.connect, name="NerdVision Main Thread")
        # Python 2.7 does not take 'daemon' as constructor argument
        self.thread.setDaemon(True)

    def start(self):
        self.thread.start()

    def connect(self):
        if self.session_id is None:
            self.logger.error("Unable to load session id for agent.")
            exit(314)
        try:
            self.grpc_service.connect(self.breakpoint_received)
        except RpcError as e:
            self.logger.error("Something went wrong with grpc connection: %s", e)

    def breakpoint_received(self, response):
        self.logger.debug("Received breakpoint request from service message_id: %s", response.message_id)
        self.breakpoint_service.process_request(response)

    def stop(self):
        self.logger.info("Stopping NerdVision")
        self.grpc_service.stop()
        self.thread.join()
        self.logger.info("NerdVision shutdown")
