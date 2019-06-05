from strongr.clouddomain.handler.abstract.cloud import AbstractDeployVmsHandler

import salt.cloud
import time

import strongr.core

import strongr.clouddomain.model.gateways

class DeployVmsHandler(AbstractDeployVmsHandler):
    def __call__(self, command):
        overrides = {}

        overrides['memory'] = command.ram * 1024
        overrides['cpu'] = command.cores
        overrides['vcpu'] = command.cores

        client = salt.cloud.CloudClient(strongr.core.Core.config().clouddomain.OpenNebula.salt_config + '/cloud')

        ret = []
        for chunked_names in self._chunk_list(command.names, 50):
            for name in chunked_names:
                vmnew_event = strongr.clouddomain.model.gateways.Gateways.inter_domain_event_factory().newVmNewEvent(name, command.cores, command.ram)
                strongr.core.Core.inter_domain_events_publisher().publish(vmnew_event)
            ret.append(client.profile(names=chunked_names, profile=command.profile, vm_overrides=overrides, parallel=True))
            #time.sleep(60) # api rate limiting removed from hpc cloud, testing with sleep turned off
            # this sleep is here because of HPCCloud API rate limiting
            # we should find a better solution at some point...

        return ret

    def _chunk_list(self, list, chunksize):
        for i in range(0, len(list), chunksize):
            yield list[i:i + chunksize]
