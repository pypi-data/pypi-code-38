import uuid

from celery.signals import worker_process_init

from strongr.core.domain.schedulerdomain import SchedulerDomain
from .wrapper import Command

import strongr.core
from celery import Celery, signals


class RunWorkerCommand(Command):
    """
    Runs a strongr worker.

    worker:run
        {--p|profile=elasticworker : The worker profile to be used}
    """
    def handle(self):
        config = strongr.core.Core.config()
        broker = config.celery.broker
        backend = config.celery.backend

        celery = Celery('strongr', broker=broker, backend=backend)

        scheduler = SchedulerDomain.schedulerService()
        scheduler.getCommandBus() # we need to initiate this as it self-registers it's commands to celery
        scheduler.getQueryBus() # we need to initiate this as it self-registers it's queries to celery

        domains = getattr(config.celery.workers, self.option('profile')).as_dict()

        commands = []
        for domain in domains:
            for command in domains[domain]:
                commands.append('{}.{}'.format(domain, command))

        for command in commands:
            strongr.core.Core.command_router().enable_worker_route_for_command(celery, command)

        workername = '%h@{}'.format(uuid.uuid4())

        argv = [
            'worker',
            '--loglevel=DEBUG',
            '-Q=' + ','.join(commands),
            #'--pool=solo',
            #'--concurrency=1',
            #'--max-tasks-per-child=1',
            '--loglevel=INFO',
            '-n {}'.format(workername)
        ]

        # crude fix for celery daemonized threads causing salt to fail
        # https://github.com/celery/celery/issues/1709
        @worker_process_init.connect
        def fix_multiprocessing(**kwargs):
            # don't be a daemon, so we can create new subprocesses
            from multiprocessing import current_process
            current_process().daemon = False

        @signals.setup_logging.connect
        def setup_celery_logging(**kwargs):
            pass

        celery.worker_main(argv)
