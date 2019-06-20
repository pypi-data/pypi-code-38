import datetime

from django.db import models

from register.dates import get_ranges_for_dates
from register.models.attendee import Attendee


class AccommNight(models.Model):
    date = models.DateField(unique=True)

    @property
    def form_name(self):
        return 'night_{}'.format(self)

    def __str__(self):
        return self.date.isoformat()

    class Meta:
        ordering = ['date']


class Accomm(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='accomm',
                                    on_delete=models.CASCADE)

    nights = models.ManyToManyField(AccommNight)
    requirements = models.TextField(blank=True)
    family_usernames = models.TextField(blank=True)
    room = models.CharField(max_length=128, blank=True, default='')

    def __str__(self):
        return 'Accomm <{}>'.format(self.attendee.user.username)

    def get_checkin_checkouts(self):
        """Get the successive check-in and check-out dates for the attendee"""
        stays = get_ranges_for_dates(
            night.date for night in self.nights.all()
        )

        for first_night, last_night in stays:
            yield first_night
            yield last_night + datetime.timedelta(days=1)

    def get_stay_details(self):
        """Get the check-in, check-out for each stay"""
        ci_co = iter(self.get_checkin_checkouts())
        return zip(ci_co, ci_co)

    def get_roommates(self):
        if self.room:
            return Attendee.objects.filter(
                accomm__room=self.room).exclude(id=self.attendee_id)
