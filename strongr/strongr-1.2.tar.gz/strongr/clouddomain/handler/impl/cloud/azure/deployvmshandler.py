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

        client = salt.cloud.CloudClient(strongr.core.Core.config().clouddomain.Azure.salt_config + '/cloud')

        ret = []
        for name in command.names:
            vmnew_event = strongr.clouddomain.model.gateways.Gateways.inter_domain_event_factory().newVmNewEvent(name, command.cores, command.ram)
            strongr.core.Core.inter_domain_events_publisher().publish(vmnew_event)
        ret.append(client.profile(names=command.names, profile=command.profile, vm_overrides=overrides, parallel=True))

        return ret
