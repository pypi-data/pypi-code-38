from strongr.clouddomain.handler.abstract.cloud import AbstractRequestJidStatusHandler

import salt.runner

import strongr.core
import strongr.core.gateways

class RequestJidStatusHandler(AbstractRequestJidStatusHandler):
    def __call__(self, query):
        opts = salt.config.master_config(strongr.core.Core.config().clouddomain.OpenNebula.salt_config + '/master')
        opts['quiet'] = True
        runner = salt.runner.RunnerClient(opts)

        cache = strongr.core.gateways.Gateways.cache()

        if not cache.exists('clouddomain.jobs.running'):
            cache.set('clouddomain.jobs.running', runner.cmd('jobs.active'), 1)

        jobs = cache.get('clouddomain.jobs.running')

        if jobs is None:
            jobs = {}

        if query.jid not in jobs: # we only want to give status when the job is finished running
            result = runner.cmd('jobs.lookup_jid', [query.jid])
            return result
        return None
