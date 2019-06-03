import cbor2
import logging
from .zmqflp_client import ZMQFLPClient  # PROD
# from zmqflp_client import FreelanceClient  # DEBUG

# Client usable with Context Managers
# needed for containerized python jobs


class ZMQFLPManagedClient(ZMQFLPClient):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        logging.debug('stopping client...')
        [x.stop() for x in self.clients]
        return False
