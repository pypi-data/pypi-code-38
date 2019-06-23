import logging

logger = logging.getLogger(__name__)


class LiveDbController(object):

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass
