import threading

import fnmatch
import salt.config
import salt.utils.event

import strongr.core

import strongr.clouddomain.factory.intradomaineventfactory
import strongr.clouddomain.factory.interdomaineventfactory
import strongr.clouddomain.model.gateways

import logging

class SaltEventTranslator(threading.Thread):
    def run(self):
        opts = salt.config.client_config(strongr.core.Core.config().clouddomain.OpenNebula.salt_config + '/master')
        inter_domain_event_factory = strongr.clouddomain.model.gateways.Gateways.inter_domain_event_factory()

        event = salt.utils.event.get_event(
            'master',
            sock_dir=opts['sock_dir'],
            transport=opts['transport'],
            opts=opts)

        while True:
            ret = event.get_event(full=True)
            if ret is None:
                continue

            try:
                if fnmatch.fnmatch(ret['tag'], 'salt/job/*/ret/*'):
                    data = ret['data']
                    if 'jid' in data and 'return' in data and 'retcode' in data:
                        job_finished_event = inter_domain_event_factory.newJobFinishedEvent(data['jid'], data['return'], data['retcode'])
                        strongr.core.Core.inter_domain_events_publisher().publish(job_finished_event)
                elif fnmatch.fnmatch(ret['tag'], 'salt/cloud/*/creating'):
                    data = ret['data']
                    if 'name' in data:
                        vmcreated_event = inter_domain_event_factory.newVmCreatedEvent(data['name'])
                        strongr.core.Core.inter_domain_events_publisher().publish(vmcreated_event)
                elif fnmatch.fnmatch(ret['tag'], 'salt/cloud/*/created'):
                    data = ret['data']
                    if 'name' in data:
                        vmready_event = inter_domain_event_factory.newVmReadyEvent(data['name'])
                        strongr.core.Core.inter_domain_events_publisher().publish(vmready_event)
                elif fnmatch.fnmatch(ret['tag'], 'salt/cloud/*/destroyed'):
                    data = ret['data']
                    if 'name' in data:
                        vmdestroyed_event = inter_domain_event_factory.newVmDestroyedEvent(data['name'])
                        strongr.core.Core.inter_domain_events_publisher().publish(vmdestroyed_event)
            except Exception as e: # thread must always continue running
                logging.getLogger('SaltEventTranslator').warning(str(e))
                pass
