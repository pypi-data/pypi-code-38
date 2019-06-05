from salt.exceptions import SaltSystemExit

from strongr.clouddomain.handler.abstract.cloud import AbstractDestroyVmsHandler

import salt.cloud
import strongr.core

import logging

class DestroyVmsHandler(AbstractDestroyVmsHandler):
    def __call__(self, command):
        client = salt.cloud.CloudClient(strongr.core.Core.config().clouddomain.Azure.salt_config + '/cloud')

        logger = logging.getLogger(self.__class__.__name__)

        ret = []

        # we are using _chunk_list generator because at some point we might want to remove more than 1 at a time
        for chunked_names in self._chunk_list(command.names, 1): # remove one by one, we are offloading this to amqp anyway
            try:
                ret.append(client.destroy(names=chunked_names))
            except SaltSystemExit as e:
                # An exception occured within salt. Normally vmdestroyed event would be published trough salt event system.
                # Assume VM is no longer there and broadcast vm destroyed event from here.
                # If it turns out the vm is still there but the error was triggered due to api rate limiting or flaky connection
                # the cleanup job will remove the vm at a later time.
                inter_domain_event_factory = strongr.clouddomain.model.gateways.Gateways.inter_domain_event_factory()
                vmdestroyed_event = inter_domain_event_factory.newVmDestroyedEvent(chunked_names[0])
                strongr.core.Core.inter_domain_events_publisher().publish(vmdestroyed_event)
                logger.warning(e)

        return ret

    def _chunk_list(self, list, chunksize):
        for i in range(0, len(list), chunksize):
            yield list[i:i + chunksize]
