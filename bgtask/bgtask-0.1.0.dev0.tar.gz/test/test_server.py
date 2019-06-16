from unittest import TestCase


class TestServer(TestCase):
    def test_start(self):
        from bgtask import Server, update_config, task
        update_config(dict(
            REDIS_HOST='127.0.0.1',
            REDIS_PORT='6379',
            TASK_QUEUE_KEY="mytask",
            TASK_WORKER=4
        ))

        @task()
        def test_func(a, b, c=1):
            print 'test'

        Server().start()

        self.assertTrue(True)
