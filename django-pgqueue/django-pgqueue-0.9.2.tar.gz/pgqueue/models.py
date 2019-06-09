from django.contrib.postgres.functions import TransactionNow
from django.contrib.postgres.fields import JSONField
from django.db import models


def lazy_empty_dict():
    return {}


class BaseJob(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=TransactionNow)
    execute_at = models.DateTimeField(default=TransactionNow)
    priority = models.PositiveIntegerField(default=0)
    context = JSONField(default=lazy_empty_dict, blank=True)
    kwargs = JSONField(default=lazy_empty_dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['-priority', 'created_at']),
        ]
        abstract = True

    def __str__(self):
        return '{} {}'.format(self.task, self.kwargs)

    def as_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'execute_at': self.execute_at,
            'priority': self.priority,
            'kwargs': self.kwargs,
            'task': self.task,
        }


class Job(BaseJob):
    pass
