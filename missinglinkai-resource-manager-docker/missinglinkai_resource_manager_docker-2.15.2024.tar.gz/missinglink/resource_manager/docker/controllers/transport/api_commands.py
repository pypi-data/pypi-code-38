import asyncio
import functools
import json
import logging
from typing import NamedTuple

from .docker_execution import DockerExecution

logger = logging.getLogger(__name__)


class CommandResponseError(Exception):
    def __init__(self, command, response):
        self.command = command
        self.response = response


async def send_command(send, command_name, command_version, **kwargs):
    await send(command=f"{command_name}:{command_version}", data=kwargs)


class RunningJob(NamedTuple):
    job_id: str
    task: asyncio.Future
    slot: list


class WsAPI:
    def __init__(self, active_config, job_completed_callback):
        self.active_config = active_config
        self.job_completed_callback = job_completed_callback
        self._running = dict()
        self.free_slots = list(active_config.general.get('slots', [None]))

    def get_running(self):
        return dict(self._running)

    def _job_done(self, job: RunningJob, task):
        logger.info(f'Job {job.job_id} completed ')
        self._running.pop(job.job_id, None)
        self.job_completed_callback(job.job_id, task)

    def _job_stared(self, job_id, task, slot):
        job: RunningJob = RunningJob(job_id=job_id, task=task, slot=slot)
        job.task.add_done_callback(functools.partial(self._job_done, job))
        self._running[job.job_id] = job

    async def register(self, send_async, **kwargs):
        from ..docker.docker_wrapper import DockerWrapper

        data = DockerWrapper.get().be_summary()
        data["gpu_present"] = self.active_config.general.get('gpu', False)
        data["capacity"] = self.active_config.general.get('capacity', 1)
        data["slots"] = self.active_config.general.get('slots', None)
        data["pull_job"] = self.active_config.general.get('pull_job')
        if self.active_config.general.get('hostname'):
            data['server'] = data.get('server', {})
            data['server']['name'] = self.active_config.general.get('hostname')

        response = await send_async(command="REGISTER:1", jwt=self.active_config.general.jwt, data=data, rpc=True)

        if response.get('ok', False):
            logger.info("Connected")
            return True
        raise CommandResponseError("register_1", response)

    async def kill(self, **kwargs):
        job_id = kwargs['invocation_id']
        running_job_task: RunningJob = self._running.get(job_id, None)

        if running_job_task is None:
            logger.warning('Job id %s is not running', job_id)
            return

        logger.info(f'Killing {job_id}: {running_job_task.task}')
        running_job_task.task.cancel()

    async def running(self, send_async=None, **kwargs):
        tasks = list(self._running.keys())
        await send_async(command='RUNNING:1', data=tasks)
        return {'ok': tasks}

    async def run(self, send_async=None, **kwargs):

        logger.debug('%s', json.dumps(kwargs))
        kwargs['active_config'] = self.active_config
        job_id = kwargs['invocation_id']
        if job_id in self._running:
            logger.warning('job %s is already running')
            return {'ok': False, 'error': 'job already running'}

        slot = self.free_slots.pop()

        def release_slot_callback(execution):
            logger.info('%s: released slot %s', execution.invocation_id, slot)
            self.free_slots.append(slot)

        task = asyncio.ensure_future(DockerExecution.create(send_async, slot=slot, release_slot_callback=release_slot_callback, **kwargs).run_manged())
        self._job_stared(job_id, task, slot)
        logger.info(f'{job_id} is now running')

        await task
        return {'ok': True, 'invocation_id': job_id}

    async def echo(self, send_async=None, **kwargs):
        logger.info('%s', json.dumps(kwargs))
        send_async(data=kwargs)
        return {'ok': True, 'kwargs': kwargs}

    async def on_connect(self, send_async=None, **kwargs):
        logger.debug('on_connect %s %s', self.active_config, kwargs)
        await send_async(jwt=self.active_config.general.jwt)

    def api_mapping(self):
        return {
            'REGISTER:1': self.register,
            'RUN:1': self.run,
            'KILL:1': self.kill,
            'RUNNING:1': self.running,
            '_on_connect': self.on_connect
        }
