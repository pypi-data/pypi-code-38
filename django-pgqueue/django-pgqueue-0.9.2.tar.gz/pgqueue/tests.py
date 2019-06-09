import time
from contextlib import contextmanager
from datetime import timedelta
from threading import Thread
from unittest import mock

from django.test import SimpleTestCase
from django.utils import timezone

from .decorators import retry, repeat
from .models import Job
from .queue import Queue
from .worker import Worker


def demo_task(queue, job):
    return job.kwargs['value']


class QueueTest(SimpleTestCase):
    allow_database_queries = True

    def setUp(self):
        self.db_objects = []
        self.queue = Queue(
            tasks={'demo_task': demo_task},
            notify_channel='demo_queue',
        )

    def tearDown(self):
        for obj in self.db_objects:
            obj.delete()

    def test_enqueue(self):
        self.queue.enqueue('demo_task', kwargs={'value': 'val1'})

        job = Job.objects.first()
        self.db_objects.append(job)
        self.assertEqual(job.task, 'demo_task')
        self.assertEqual(job.kwargs, {'value': 'val1'})

    def test_enqueue_once(self):
        old_job = Job.objects.create(task='demo_task', kwargs={'value': 'val1'})
        job_1 = self.queue.enqueue_once('demo_task', {'value': 'val1'})
        self.assertEqual(job_1.id, old_job.id)
        job_2 = self.queue.enqueue_once('demo_task', {'value': 'val2'})
        self.assertNotEqual(job_2, old_job.id)

    def test_dequeue(self):
        job1 = Job.objects.create(task='demo_task')
        job2 = Job.objects.create(task='demo_task')
        self.db_objects += [job1, job2]
        self.assertEqual(job1.id, self.queue.dequeue().id)
        self.assertEqual(job2.id, self.queue.dequeue().id)

    def test_run_job(self):
        job = Job.objects.create(task='demo_task', kwargs={'value': 'hello'})
        self.db_objects.append(job)
        retval = self.queue.run_job(job)
        self.assertEqual(retval, 'hello')

    def test_listen_notify(self):
        self.queue.listen()

        job = Job.objects.create(task='demo_task', kwargs={'value': 'hello'})
        self.db_objects.append(job)
        self.queue.notify(job)

        notifies = self.queue.wait(1)
        notify = notifies[0]

        self.assertEqual(notify.channel, 'demo_queue')
        self.assertEqual(notify.payload, str(job.id))


class WorkerTest(SimpleTestCase):
    allow_database_queries = True

    class DemoWorker(Worker):
        wait_timeout = 1

        def __init__(self, queue, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.queue = queue

        def start(self):
            super().start()

            # Close database connection when worker is stopped
            # top prevent "database is being accessed by other users".
            from django.db import connection
            connection.close()

        def stop(self):
            self._shutdown = True

        def bind_signals(self):
            # Signals doesn't work if the worker is running not in
            # the main thread, also there are no signals during
            # tests running so let’s ignore them.
            pass

    def setUp(self):
        self.db_objects = []

    def tearDown(self):
        for obj in self.db_objects:
            obj.delete()

    @contextmanager
    def start_worker(self, queue):
        worker = self.DemoWorker(queue)
        thread = Thread(target=worker.start, daemon=True)
        thread.start()
        yield worker
        time.sleep(1)  # wait worker to finish the tasks
        worker.stop()
        thread.join()

    def test_enqueue(self):
        queue = Queue(
            tasks={
                'task1': mock.Mock(),
                'task2': mock.Mock(),
            },
            notify_channel='test_channel',
        )

        with self.start_worker(queue):
            job1 = queue.enqueue('task1')
            job2 = queue.enqueue('task2')
            self.db_objects += [job1, job2]

        queue.tasks['task1'].assert_called()
        queue.tasks['task2'].assert_called()


class RepeatDecoratorTest(SimpleTestCase):
    allow_database_queries = True

    def tearDown(self):
        Job.objects.all().delete()

    def test_repeat(self):
        task = mock.Mock()
        wrapped_task = repeat(timedelta(minutes=1))(task)

        queue = Queue(tasks={'task': wrapped_task}, notify_channel='test_channel')
        job = Job(task='task')  # job should not be saved in database to simulate dequeue call
        wrapped_task(queue, job)

        new_job = Job.objects.last()
        delta = new_job.execute_at - timezone.now()
        self.assertAlmostEqual(delta.total_seconds(), timedelta(minutes=1).total_seconds(), places=1)


class RetryDecoratorTest(SimpleTestCase):
    allow_database_queries = True

    def tearDown(self):
        Job.objects.all().delete()

    def test_retry(self):
        task = mock.Mock()
        task.side_effect = Exception()
        wrapped_task = retry([Exception], delay=timedelta(seconds=1), max_attempts=3)(task)

        queue = Queue(tasks={'task': task}, notify_channel='test_channel')
        job = Job.objects.create(task='task')

        wrapped_task(queue, job)
        retry_job = Job.objects.last()

        self.assertEqual(retry_job.task, 'task')
        self.assertEqual(retry_job.context['retry_attempt'], 1)

    def test_retry_delay(self):
        task = mock.Mock()
        task.side_effect = Exception()
        wrapped_task = retry([Exception], delay=timedelta(seconds=10), max_attempts=10)(task)

        queue = Queue(tasks={'task': task}, notify_channel='test_channel')
        job = Job.objects.create(task='task')

        for n in range(10):
            wrapped_task(queue, job)
            job = Job.objects.order_by('created_at').last()
            delta = job.execute_at - timezone.now()
            self.assertAlmostEqual(delta.total_seconds(), timedelta(seconds=10).total_seconds(), places=1)

        jobs = Job.objects.all()
        self.assertEqual(jobs.count(), 11)

    def test_retry_max_attempts(self):
        task = mock.Mock()
        task.side_effect = Exception()
        wrapped_task = retry([Exception], delay=timedelta(seconds=1), max_attempts=10)(task)

        queue = Queue(tasks={'task': task}, notify_channel='test_channel')
        job = Job.objects.create(task='task')

        for n in range(10):
            wrapped_task(queue, job)
            job = Job.objects.order_by('created_at').last()
            self.assertEqual(job.context['retry_attempt'], n + 1)

        with self.assertRaises(Exception):
            wrapped_task(queue, job)

        jobs = Job.objects.all()
        self.assertEqual(jobs.count(), 11)
