from django.db import models

from register.models import Attendee


class CheckIn(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='check_in',
                                    on_delete=models.PROTECT)
    t_shirt = models.BooleanField(default=False)
    shoes = models.BooleanField(default=False)
    swag = models.BooleanField(default=False)
    nametag = models.BooleanField(default=False)
    key_card = models.CharField(max_length=5, blank=True)
    room_key = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    returned_key = models.BooleanField(default=False)
    returned_card = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
