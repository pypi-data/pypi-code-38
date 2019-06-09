import select
import logging
import time

from django.utils import translation
from django.db import connection

from .models import Job


class Queue:
    job_model = Job
    logger = logging.getLogger(__name__)

    def __init__(self, tasks, notify_channel):
        self.tasks = tasks
        self.notify_channel = notify_channel

    def notify(self, job):
        with connection.cursor() as cur:
            cur.execute('NOTIFY "{}", %s;'.format(self.notify_channel), [str(job.pk)])

    def get_job_context(self):
        language = translation.get_language()
        return {'language': language}

    def in_atomic_block(self):
        return connection.in_atomic_block

    def enqueue(self, task, kwargs=None, execute_at=None, priority=0, context=None):
        assert not self.in_atomic_block(), 'Task cannot be executed inside a trasnaction'
        assert task in self.tasks, 'Task "{}" not found in the task list'
        kwargs = kwargs or {}

        job_context = self.get_job_context()
        if context is not None:
            job_context.update(context)

        job = Job(
            task=task,
            kwargs=kwargs,
            priority=priority,
            context=job_context,
        )
        if execute_at:
            job.execute_at = execute_at
        job.save()

        if self.notify_channel:
            self.notify(job)

        self.logger.info('New job scheduled %r', job)
        return job

    def enqueue_once(self, task, kwargs=None, *args_, **kwargs_):
        job = self.job_model.objects.filter(task=task, kwargs=kwargs or {}).first()
        if job is not None:
            return job
        return self.enqueue(task, kwargs, *args_, **kwargs_)

    def listen(self):
        with connection.cursor() as cur:
            cur.execute('LISTEN "{}";'.format(self.notify_channel))

    def wait(self, timeout):
        connection.connection.poll()
        notifies = self._get_notifies()
        if notifies:
            return notifies

        select.select([connection.connection], [], [], timeout)
        connection.connection.poll()
        return self._get_notifies()

    def _get_notifies(self):
        notifies = [
            i for i in connection.connection.notifies
            if i.channel == self.notify_channel]

        connection.connection.notifies = [
            i for i in connection.connection.notifies
            if i.channel != self.notify_channel]

        return notifies

    def dequeue(self):
        query = """
        DELETE FROM {table}
        WHERE id = (
            SELECT id
            FROM {table}
            WHERE execute_at <= NOW()
            ORDER BY priority DESC, created_at, id
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING *;
        """
        query = query.format(table=self.job_model._meta.db_table)
        results = list(self.job_model.objects.raw(query))
        assert len(results) <= 1

        if not results:
            return None

        return results[0]

    def run_job(self, job):
        language = job.context.get('language')
        with translation.override(language):
            return self._run_job(job)

    def _run_job(self, job):
        task = self.tasks[job.task]
        start_time = time.time()
        retval = task(self, job)
        self.logger.info(
            'Processing %r took %0.4f seconds. Task returned %r.',
            job, time.time() - start_time, retval,
            extra={
                'data': {
                    'job': job.as_dict(),
                    'retval': retval,
                },
            },
        )
        return retval
