from rook.services.logging_location_service import LoggingLocationService


class LocationLogHandler(object):

    NAME = 'log_handler'

    def __init__(self, arguments, processor_factory):
        self.logger = arguments['logger']

    def add_aug(self, trigger_services, output, aug):
        trigger_services.get_service(LoggingLocationService.NAME).add_logging_aug(self.logger, aug)
