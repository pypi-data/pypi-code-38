from strongr.clouddomain.handler.abstract.cloud import AbstractRunJobHandler
import strongr.core

import salt.client

class RunJobHandler(AbstractRunJobHandler):
    def __call__(self, command):
        local = salt.client.LocalClient()
        local.cmd_async(command.host, 'cmd.run', ['cmd={}'.format(command.script), 'runas={}'.format(strongr.core.Core.config().clouddomain.OpenNebula.runas)], jid=command.job_id)
