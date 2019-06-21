# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from aparnik.packages.shops.payments.models import Payment

# Create your models here.


class BankManager(models.Manager):
    def get_queryset(self):
        return super(BankManager, self).get_queryset()

    def get_this_user(self, user):
        if not user.is_authenticated:
            return Bank.objects.none()
        return self.get_queryset().filter(payment__user=user)

    def get_this_success(self):
        return self.get_queryset().filter(Q(ref_id='-1'))


class Bank(models.Model):

    TRANSACTION_SUCCESS = 100
    TRANSACTION_SUBMITTED = 101
    TRANSACTION_FAILED = 102
    TRANSACTION_FAILED_BY_USER = -1
    TRANSACTION_WAITING = -2

    TRANSACTION_STATUS = (
        (TRANSACTION_SUCCESS, _('Success')),
        (TRANSACTION_SUBMITTED, _('Submitted')),
        (TRANSACTION_FAILED, _('Failed')),
        (TRANSACTION_FAILED_BY_USER, _('Cancel By User')),
        (TRANSACTION_WAITING, _('Waiting for pay')),
    )

    status = models.IntegerField(
        verbose_name=_('Status'),
        # choices=TRANSACTION_STATUS,
        default=-2
    )

    authority_id = models.CharField(
        max_length=255,
        verbose_name=_('Authority ID')
    )

    ref_id = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_('Bank Reference ID')
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        verbose_name=_('Payment')
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    update_at = models.DateTimeField(
        verbose_name=_('Update At'),
        auto_now=True
    )

    objects = BankManager()

    def __str__(self):
        return '{}'.format(self.ref_id)

    def __init__(self, *args, **kwargs):
        super(Bank, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Bank, self).save(*args, **kwargs)
