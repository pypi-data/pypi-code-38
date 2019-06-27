# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager


User = get_user_model()


# TODO: send notification when change available in course or etc.
# Product Sharing
class NotifyMeManager(BaseModelManager):
    def get_queryset(self):
        return super(NotifyMeManager, self).get_queryset()

    def active(self):
        return super(NotifyMeManager, self).active().filter(is_active=True)

    def this_user(self, user):
        if not user.is_authenticated:
            return NotifyMe.objects.none()
        return self.active().filter(user_obj=user)


class NotifyMe(BaseModel):

    user_obj = models.ForeignKey(User, related_name='notifyme_user', on_delete=models.CASCADE, verbose_name=_('User'))
    model_obj = models.ForeignKey(BaseModel, related_name='notifyme_model', on_delete=models.CASCADE, verbose_name=_('Model'))
    is_active = models.BooleanField(default=False, verbose_name=_('Is Active'))

    objects = NotifyMeManager()

    class Meta:
        verbose_name = _('Notify Me')
        verbose_name_plural = _('Notifies Me')

    def __str__(self):
        return str(self.user_obj)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.id:
            self.update_needed = True
        # TODO: send Notif
        return super(NotifyMe, self).save(*args, **kwargs)
