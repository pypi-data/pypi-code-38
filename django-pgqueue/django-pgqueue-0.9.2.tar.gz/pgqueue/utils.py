from unittest import mock


def call_task(task, kwargs):
    job = mock.Mock()
    job.kwargs = kwargs
    queue = mock.Mock()
    return task(queue, job)
