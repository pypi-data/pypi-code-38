from unittest import TestCase
import time


class TestTask(TestCase):
    def test_run(self):
        from bgtask import task, update_config

        update_config(dict(
            REDIS_HOST='127.0.0.1',
            REDIS_PORT='6379',
            TASK_QUEUE_KEY="mytask",
            TASK_WORKER=2
        ))

        @task()
        def test_func(a, b, c=1):
            print 'test'

        test_func.delay("a", "b")

        self.assertTrue(True)
