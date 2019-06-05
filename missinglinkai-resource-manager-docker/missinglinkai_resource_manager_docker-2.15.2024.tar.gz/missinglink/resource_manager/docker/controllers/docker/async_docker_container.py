import asyncio
import logging

from .docker_wrapper import DockerWrapper
from .log_generator import LogGenerator
from .stat_generator import StatGenerator
from missinglink.resource_manager.docker.sync_async_tools import run_blocking_code_in_thread
from missinglink.legit.path_utils import normalize_path

logger = logging.getLogger(__name__)


class AsyncDockerContainer(object):
    @classmethod
    def get_container_env(cls, active_config):
        res = {'ML': 'True'}
        if active_config:
            res.update({
                'ML': 'True',
                'ML_CLUSTER_ID': active_config.general.cluster_id,
                'ML_CLUSTER_MANAGER': active_config.general.ws_server,
                'ML_SERVER_NAME': active_config.general.get('hostname')
            })
        return res

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    async def create_and_run(cls, **kwargs):
        run_prefix = kwargs.pop('prefix', kwargs['image'])
        return await cls.create(**kwargs).run_with_callbacks(run_prefix)

    def __init__(self, **kwargs):
        self.active_config = kwargs.pop('active_config', None)
        internal_env = self.get_container_env(self.active_config)
        self.stage_name = kwargs.pop('stage_name', None)
        self.job_id = kwargs.pop('job_id', '')
        self.loop = kwargs.pop('loop', asyncio.get_event_loop())
        env = kwargs.pop('env', {})
        env.update(internal_env)
        labels = kwargs.pop('labels', {})
        labels.update(internal_env)
        labels['ML_STAGE_NAME'] = self.stage_name
        labels['ML_JOB_ID'] = self.job_id
        self.image = kwargs.pop('image')
        self.command = kwargs.pop('command', None)
        self.env = env
        self.volumes = kwargs.pop('volumes', {})
        self.labels = labels
        self.container = None
        self.exit = None
        self.container_id = None
        self.logs = None
        self.kill_on_exit = kwargs.pop('kill_on_exit', False)
        self.work_dir = kwargs.pop('workdir', None)
        self.runtime = None
        self.docker = kwargs.pop('docker_client', DockerWrapper.get())
        if kwargs.pop('gpu', False):
            self.runtime = 'nvidia'
        self.log_cb = self.safe_get_callback(kwargs.pop('log_callback', None))
        self.stats_cb = self.safe_get_callback(kwargs.pop('stats_call_back', None), 5)
        self.logs_task = None
        self.stats_task = None
        self.waiter = None

    def __aiter__(self):
        return self

    @classmethod
    def safe_get_callback(cls, cb, empty_sleep=0):
        async def empty_func(*args, **kwargs):
            await asyncio.sleep(empty_sleep)

        return cb or empty_func

    def _get_volumes(self):
        volumes = dict(self.volumes)
        for s, t in self.active_config.general.mount.items():
            logger.debug('Adding configured mapping %s => %s', s, t)
            volumes[s] = {'bind': normalize_path(t)}

        return volumes

    async def __aenter__(self):
        service_data = self.docker.be_summary()
        max_memory = int(service_data['cpu']['memory'] * 0.9)
        volumes = self._get_volumes()
        env = dict(self.active_config.general.env)
        env.update(self.env)
        container_args = {
            'image': self.image,
            'command': self.command,
            'stdin_open': False,
            'detach': True,
            'environment': env,
            'labels': self.labels,
            'volumes': volumes,
            'working_dir': self.work_dir,
            'mem_limit': max_memory,
            'runtime': self.runtime,
            'ipc_mode': 'host',
        }

        logger.debug('Creating container with args: %s', container_args)

        self.container = self.docker.create_container(**container_args)
        self.container_id = self.container.name
        self.container.start()
        self.logs = LogGenerator(self.container, name=self.stage_name)
        self.stats_generator = StatGenerator(self.container, name=self.stage_name)

        return self

    def remove_and_cleanup_container(self):
        container_volumes = self.container.attrs.get('Mounts', [])
        self.container.remove()
        for cont_volume in container_volumes:
            if 'Name' not in cont_volume:
                logger.debug('remove_and_cleanup_container: Skipping %s ', cont_volume)
                continue

            name = cont_volume['Name']
            if name not in self.volumes:
                volume_obj = self.docker.volume(name)
                if volume_obj is not None:
                    volume_obj.remove()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.container is None:
            logger.error(f'Failed to obtain container status for {self.container_id}, container not found')
            return
        is_cancelled = exc_type is not None and exc_type is asyncio.CancelledError
        if is_cancelled:
            exc_type = None

        logger.debug(f"{self.container_id}:  __aexit__ state {self.container_id}: {self.container.status}")
        self.exit_container(force_cancel=is_cancelled)

        if self.exit is not None:
            self.remove_and_cleanup_container()
        else:
            logger.warning(f"{self.container_id}:  __aexit__ container still {self.container_id}: {self.container.status}")
        await asyncio.sleep(0)
        return exc_type is None

    def exit_container(self, force_cancel=False):
        self.container.reload()
        if self.container.status == 'running' and (force_cancel or self.kill_on_exit):
            logger.debug('%s: DOCKER: execution cancelled', self.container.name)
            self.container.kill()
            self.container.reload()
        if self.container.status != 'running':
            self.exit = (self.container.status, self.container.wait())

        self._cancel_futures(self.logs_task, self.stats_task)

    @classmethod
    def _cancel_futures(cls, *args):
        for future in args:
            if future:
                future.cancel()

    async def run_with_callbacks(self, prefix):

        async with self as context:
            logger.debug('%s: DOCKER: run %s', self.container.name, prefix)

            async def _do_stats():
                async for x in context.stats_generator:
                    await  asyncio.sleep(0)
                    await context.stats_cb(x)

            self.stats_task = asyncio.ensure_future(_do_stats(), loop=self.loop)

            async def _do_logs(stats_task: asyncio.Future):
                async for line in context.logs:
                    await  asyncio.sleep(0)
                    await  context.log_cb(line[1], step_name=line[0])

                if not stats_task.done():
                    logger.debug('%s: Logs done, canceling stats', self.container.name)
                    stats_task.cancel()

            self.logs_task = asyncio.ensure_future(_do_logs(self.stats_task), loop=self.loop)

            self.waiter = run_blocking_code_in_thread(lambda: self.container.wait(), logger=logger, loop=self.loop)
            await  asyncio.wait([self.logs_task, self.stats_task, self.waiter])
            await  run_blocking_code_in_thread(self.container.reload, logger=logger, loop=self.loop)
            logger.debug('%s: DOCKER: DONE %s', self.container.name, self.waiter.result())

        return self
