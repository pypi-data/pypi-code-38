from django.db import models

from register.models.attendee import Attendee


class ChildCare(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='child_care',
                                    on_delete=models.CASCADE)

    needs = models.TextField(blank=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return 'ChildCare <{}>'.format(self.attendee.user.username)
