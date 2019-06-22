# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.urls import reverse

from django_enumfield import enum

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.packages.shops.products.models import Product


User = get_user_model()


# Create your models here.
class NotificationType(enum.Enum):
    SYSTEM = 0
    SINGLE_USER = 1
    ALL_USER = 2

    labels = {
        SYSTEM: _('System'),
        SINGLE_USER: _('Single User'),
        ALL_USER: _('All User')
    }


class NotificationManager(BaseModelManager):

    def get_queryset(self):
        return super(NotificationManager, self).get_queryset()

    def notification_type(self, type):
        return self.get_queryset().filter(notification_send_type=type)

    def get_this_user(self, user):
        if not user.is_authenticated:
            return Notification.objects.none()
        return self.get_queryset().filter(membership__user=user).distinct().order_by('-created_at')

    def unread(self, user):
        # Remember (membership__user=user, membership__is_read=False) should must be in one prantisis.
        if not user.is_authenticated:
            return Notification.objects.none()
        return self.active().filter(membership__user=user, membership__is_read=False).order_by('-created_at')

    def unread_count(self, user):
        if not user.is_authenticated:
            return Notification.objects.none()

        return self.unread(user=user).count()

    def read(self, user):
        if not user.is_authenticated:
            return Notification.objects.none()

        read = self.unread(user=user)
        for r in read:
            r.read(user=user)
        return read.count()

    def send_notification(self, users, type, title, description, from_user_obj=None, model_obj=None):
        if users is None:
            return None
        notification = Notification.objects.create(
            type=type,
            title=title,
            description=description,
            update_needed=True,
            from_user_obj=from_user_obj,
            model_obj=model_obj,
            notification_send_type=NotificationType.SYSTEM,
        )
        for user in users:
            m = Membership(user=user, notification=notification)
            m.save()
        return notification


class Notification(BaseModel):
    NOTIFICATION_INFO = 'i'
    NOTIFICATION_SUCCESS = 's'
    NOTIFICAITON_WARNING = 'w'
    NOTIFICAITON_ERROR = 'e'

    NOTIFICATION_TYPE = (
        (NOTIFICATION_INFO, 'اطلاعات'),
        (NOTIFICATION_SUCCESS, 'موفقیت'),
        (NOTIFICAITON_WARNING, 'هشدار'),
        (NOTIFICAITON_ERROR, 'خطا')
    )
    from_user_obj = models.ForeignKey(User, related_name='notificaiton_from_user', null=True, blank=True, on_delete=models.CASCADE, verbose_name='از کاربر')
    users = models.ManyToManyField(User, through='Membership', verbose_name=_('Membership'))
    title = models.CharField(max_length=50, verbose_name=_('Title'))
    description = models.CharField(max_length=255, verbose_name=_('Message'))
    type = models.CharField(max_length=1, choices=NOTIFICATION_TYPE, verbose_name=_('Type'))
    notification_send_type = enum.EnumField(NotificationType, default=NotificationType.ALL_USER, verbose_name=_('Notification send type'))
    model_obj = models.ForeignKey(BaseModel, related_name='notification_model_obj', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Model'))
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Datetime'))
    products_buy = models.ManyToManyField(Product, blank=True, related_name='notification_products_buy', verbose_name=_('Purchase specific products'))
    products_buy_did_not = models.ManyToManyField(Product, blank=True, related_name='notification_products_buy_did_not', verbose_name=_('Did not purchase specific products '))
    description_for_admin = models.TextField(blank=True, null=True, verbose_name=_('Description for admin'))
    sent_result = models.TextField(blank=True, null=True, verbose_name=_('Sent result'))

    objects = NotificationManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def save(self, *args, **kwargs):
        if not self.id:
            self.update_needed = True
        return super(Notification, self).save(*args, **kwargs)

    def get_notification_type_json_display(self):

        icon = ""

        if self.type == self.NOTIFICATION_INFO:

            icon = "http://www.freeiconspng.com/uploads/info-icon-7.png"
        elif self.type == self.NOTIFICATION_SUCCESS:

            icon = "http://www.freeiconspng.com/uploads/success-icon-10.png"
        elif self.type == self.NOTIFICAITON_WARNING:

            icon = "http://www.freeiconspng.com/uploads/black-warning-icon-20.png"
        elif self.type == self.NOTIFICAITON_ERROR:

            icon = "http://www.freeiconspng.com/uploads/error-icon-4.png"
        json = {
            'icon': icon,
            'name': self.get_type_display()
        }
        return json

    def get_user(self):
        return self.users.first()

    def get_user_is_read(self, user):
        return self.membership_set.filter(user=user).first().is_read

    def read(self, user):
        return self.membership_set.filter(user=user, is_read=False).update(is_read=True)

    def get_api_read_uri(self):
        return reverse('aparnik-api:notifications:read', args=[self.id])


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, verbose_name=_('Notification'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')


class NotificaitonForSingleUserManager(NotificationManager):
    pass


class NotificationForSingleUser(Notification):
    objects = NotificaitonForSingleUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Notification For Single User')
        verbose_name_plural = _('Notifications For Single User')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.notification_send_type = NotificationType.SINGLE_USER
        return super(NotificationForSingleUser, self).save(*args, **kwargs)


class NotificaitonSystemManager(NotificationManager):
    pass


class NotificationSystem(Notification):

    objects = NotificaitonSystemManager()

    class Meta:
        proxy = True
        verbose_name = _('Notification System')
        verbose_name_plural = _('Notifications System')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.notification_send_type = NotificationType.SYSTEM
        return super(NotificationSystem, self).save(*args, **kwargs)
