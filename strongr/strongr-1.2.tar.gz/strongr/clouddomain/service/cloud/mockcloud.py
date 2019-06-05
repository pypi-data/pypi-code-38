from strongr.clouddomain.model.gateways import Gateways
from .abstractcloudservice import AbstractCloudService

from strongr.clouddomain.handler.impl.cloud.mockcloud import ListDeployedVmsHandler, RunJobHandler, DeployVmsHandler

import subprocess
import threading
import strongr.core

class MockCloud(AbstractCloudService):
    def __init__(self, *args, **kwargs):
        super(MockCloud, self).__init__(*args, **kwargs)
        self._check_docker()
        thread = threading.Thread(target=self._publish_localhost)  # run in separate thread so it doesn't block strongr
        thread.start()

    def _publish_localhost(self):
        import time
        import psutil

        time.sleep(5)

        inter_domain_event_factory = Gateways.inter_domain_event_factory()
        inter_domain_events_publisher = strongr.core.Core.inter_domain_events_publisher()

        vmnew_event = inter_domain_event_factory.newVmNewEvent('localhost', psutil.cpu_count(logical=True), psutil.virtual_memory().total / 1024 / 1024 / 1024)
        inter_domain_events_publisher.publish(vmnew_event)

        time.sleep(1)
        vmcreated_event = inter_domain_event_factory.newVmCreatedEvent('localhost')
        inter_domain_events_publisher.publish(vmcreated_event)

        time.sleep(1)
        vmready_event = inter_domain_event_factory.newVmReadyEvent('localhost')
        inter_domain_events_publisher.publish(vmready_event)


    def _check_docker(self):
        ret_code = subprocess.call('docker ps', shell=True)
        if ret_code != 0:
            raise Exception("Can't access docker sock. Is docker installed? Do you have sufficient privileges?")

    def get_command_handlers(self):
        return [RunJobHandler, DeployVmsHandler]

    def get_query_handlers(self):
        return [ListDeployedVmsHandler]
