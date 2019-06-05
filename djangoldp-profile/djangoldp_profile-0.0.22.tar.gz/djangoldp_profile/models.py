from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoldp.models import Model


class Profile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    available = models.NullBooleanField(blank=True)
    bio = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)

    def jabberID(self):
        try:
            return self.user.chatProfile.jabberID
        except:
            return None

    class Meta:
        auto_author = 'user'
        permissions = (
            ('view_member', 'Read'),
            ('control_member', 'Control'),
        )
        depth = 0

    def __str__(self):
        return '{} ({})'.format(self.user.get_full_name(), self.user.username)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
