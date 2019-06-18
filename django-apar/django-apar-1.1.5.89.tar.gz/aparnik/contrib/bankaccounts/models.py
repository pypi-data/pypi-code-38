# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from aparnik.utils.fields import *
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager

User = get_user_model()


# Create your models here.
class BankNameManager(BaseModelManager):

    def get_queryset(self):
        return super(BankNameManager, self).get_queryset()

    def active(self):
        return super(BankNameManager, self).active().filter(is_active=True)


class BankName(BaseModel):

    title = models.CharField(max_length=255, verbose_name=_('Title'))

    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = BankNameManager()

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(BankName, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Bank Name')
        verbose_name_plural = _('Bank Names')


class BankAccountManager(BaseModelManager):

    def get_queryset(self):
        return super(BankAccountManager, self).get_queryset()

    def active(self):
        return super(BankAccountManager, self).active().filter(is_active=True)

    def this_user(self, user):
        if not user.is_authenticated:
            return BankAccount.objects.none()
        return self.active().filter(user_obj=user)


class BankAccount(BaseModel):

    user_obj = models.ForeignKey(User, related_name='bankaccounts', on_delete=models.CASCADE, verbose_name=_('User'))
    bank_name_obj = models.ForeignKey(BankName, related_name='bankaccounts_name', on_delete=models.CASCADE, verbose_name=_('Bank Name'))
    account_number = models.CharField(max_length=255, verbose_name=_('Account Number'))
    card_number = models.CharField(max_length=16, verbose_name=_('Card Number'))
    shaba_number = models.CharField(max_length=255, unique=True, verbose_name=_('Shaba Number'))
    is_default = models.BooleanField(default=False, verbose_name=_('Is default'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = BankAccountManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        if BankAccount.objects.active().filter(user_obj=self.user_obj, is_default=True).count() == 0:
            self.is_default = True
        return super(BankAccount, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user_obj)

    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')

    def set_is_default(self, user):
        if self.user_obj == user:
            BankAccount.objects.this_user(user=user).update(is_default=False)
            self.is_default = True
            self.save()
            return True
        return False
