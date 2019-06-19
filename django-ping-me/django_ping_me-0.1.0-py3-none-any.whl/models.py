from django.conf import settings
from django.db import models
import datetime


class Domain(models.Model):
    url = models.CharField(verbose_name='Adresse', max_length=255)
    description = models.CharField(verbose_name='Description', max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @property
    def last_ping(self):
        return Ping.objects.filter(domain=self).latest('date')

    @property
    def last_month_summary(self):
        date = datetime.date.today().replace(day=1)
        date = date - datetime.timedelta(days=1)
        date = date.replace(day=1)
        return PingSummary.objects.get(domain=self, date=date)

    @property
    def current_month_summary(self):
        summary = PingSummary(domain=self)
        summary.date = datetime.date.today().replace(day=1)
        all_pings = Ping.objects.filter(domain=self, date__gte=summary.date)
        for ping in all_pings:
            if ping.success:
                summary.nb_success += 1
            else:
                summary.nb_errors += 1
        return summary

    def __str__(self):
        desc = self.description
        if self.user.email:
            desc += " - " + self.user.email
        return "{} ({})".format(self.url, desc)


class Ping(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    address = models.GenericIPAddressField()
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)

    def __str__(self):
        success = 'success' if self.success else 'fail'
        return "{:%Y-%m-%d %H:%M:%S} - {} - {} - {}"\
            .format(self.date, self.domain.url, self.address, success)


class PingSummary(models.Model):
    date = models.DateField()
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    nb_success = models.IntegerField(default=0)
    nb_errors = models.IntegerField(default=0)

    @property
    def nb_attempt(self):
        return self.nb_success + self.nb_errors

    @property
    def percentage(self):
        if self.nb_attempt <= 0:
            return 0
        return self.nb_success * 100 / self.nb_attempt

    def to_str(self):
        return "{:,} succès et {:,} échecs"\
            .format(self.nb_success, self.nb_errors)\
            .replace(',', ' ')

    def __str__(self):
        return "{:%Y:%m} - {} - {}"\
            .format(self.date, self.domain.url, self.to_str())