from rook.services.http_server_services.http_server_services import HttpServerService


class HttpServerHandler(object):

    NAME = 'http_server'

    def __init__(self, arguments, processor_factory):
        return

    def add_aug(self, trigger_services, output, aug):
        trigger_services.get_service(HttpServerService.NAME).add_logging_aug(aug)
