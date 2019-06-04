from django.db import models
from django.utils.functional import cached_property

from register.models.attendee import Attendee


class Queue(models.Model):
    name = models.CharField(max_length=32, db_index=True)
    size = models.IntegerField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class QueueSlot(models.Model):
    attendee = models.ForeignKey(Attendee, related_name='queues',
                                 on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, related_name='slots',
                              on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    @cached_property
    def position(self):
        return QueueSlot.objects.filter(
            queue=self.queue, timestamp__lt=self.timestamp).count() + 1

    def __str__(self):
        return '{}: {} ({})'.format(
            self.queue.name, self.position, self.attendee.user.username)

    class Meta:
        ordering = ['timestamp']
        unique_together = ('attendee', 'queue')
