# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from aparnik.utils.formattings import formatprice
from aparnik.utils.fields import *
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager

User = get_user_model()


# Create your models here.
class UserAddressManager(BaseModelManager):

    def get_queryset(self):
        return super(UserAddressManager, self).get_queryset()

    def active(self):
        return super(UserAddressManager, self).active().filter(is_active=True)

    def this_user(self, user):
        if not user.is_authenticated:
            return UserAddress.objects.none()
        return self.active().filter(user_obj=user)

    def default(self):
        return self.active().filter(is_default=True).first()


class UserAddress(BaseModel):

    user_obj = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE, verbose_name=_('User'))
    city_obj = models.ForeignKey('province.City', related_name='addresses', on_delete=models.CASCADE, verbose_name=_('City'))
    # location = models.
    address = models.TextField(verbose_name=_('Address'))
    postal_code = PostalCodeField(null=True, blank=True, verbose_name=_('Postal code'))
    phone = PhoneField(mobile=False, null=True, blank=True, verbose_name=_('Phone'))

    is_default = models.BooleanField(default=False, verbose_name=_('Is default'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = UserAddressManager()

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(UserAddress, self).save(*args, **kwargs)

    # TODO: Returning user object is not suitable, since one user might have several address. A more in
    # informative field needed.
    def __str__(self):
        return str(self.user_obj)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def set_is_default(self, user):
        if self.user_obj == user:
            UserAddress.objects.this_user(user=user).update(is_default=False)
            self.is_default = True
            self.save()
            return True
        return False

