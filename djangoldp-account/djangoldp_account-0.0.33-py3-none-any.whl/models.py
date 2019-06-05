import validators
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy

from djangoldp.models import Model


def name(self):
    return self.get_full_name()


def webid(self):
    # hack : We user webid as username for external user (since it's an uniq identifier too)
    if validators.url(self.username):
        webid = self.username
    else:
        webid = '{0}{1}'.format(settings.BASE_URL, reverse_lazy('user-detail', kwargs={'pk': self.pk}))
    return webid


user_model = get_user_model()
user_model.name = name
user_model.webid = webid


class Account(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    picture = models.URLField(blank=True, null=True)
    issuer = models.URLField(blank=True, null=True)

    class Meta:
        depth = 0
        auto_author = 'user'
        permissions = (
            ('view_account', 'Read'),
            ('control_account', 'Control'),
        )

    def __str__(self):
        return '{} ({})'.format(self.user.get_full_name(), self.user.username)


class ChatProfile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chatProfile")
    jabberID = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        depth = 0
        auto_author = 'user'
        permissions = (
            ('view_chatprofile', 'Read'),
            ('control_chatprofile', 'Control'),
        )

    def __str__(self):
        return '{} (jabberID: {})'.format(self.user.get_full_name(), self.jabberID)


class OPClient(Model):
    issuer = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    def __str__(self):
        return '{} ({})'.format(self.issuer, self.client_id)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
        chat_profile = ChatProfile.objects.create(user=instance)
        if settings.JABBER_DEFAULT_HOST:
            chat_profile.jabberID = '{}@{}'.format(instance.username, settings.JABBER_DEFAULT_HOST)
            chat_profile.save()
    else:
        try:
            instance.account.save()
        except:
            pass
