# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from aparnik.contrib.users.models import PhoneField
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.text import Truncator

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.notifications.models import Notification

User = get_user_model()


# Create your models here.
class ContactUsManager(BaseModelManager):
    def get_queryset(self):
        return super(ContactUsManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)


class ContactUs(BaseModel):
    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Website')
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Address')
    )

    phone = PhoneField(
        mobile=True,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email')
    )

    first_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('First name')
    )

    last_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Last name')
    )

    title = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Title')
    )

    content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Content'),
    )

    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True
    )

    objects = ContactUsManager()

    def save(self, *args, **kwargs):

        return super(ContactUs, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ContactUs, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return '%s %s' % (self.id, self.title)

    class Meta:
        # ordering = ['latitude', 'longitude']
        verbose_name = _('Contact Us')
        verbose_name_plural = _('Contact Us')

    def get_api_uri(self):
        return reverse('aparnik-api:contactus:details', args=[self.id])

    def get_title(self):
        return self.title


def post_save_constact_us_receiver(sender, instance, created, *args, **kwargs):

    users = User.objects.none()
    verbose_name = instance._meta.verbose_name
    title = '%s %s درج کرد' % (instance.last_name, verbose_name )
    description = Truncator(instance.get_title() + ' ' + instance.content).words(30)

    # admin
    users = User.objects.admins()

    if created:
        Notification.objects.send_notification(
            users=users,
            type=Notification.NOTIFICATION_INFO,
            title=title,
            description=description,
            model_obj=instance,
        )


post_save.connect(post_save_constact_us_receiver, sender=ContactUs)
