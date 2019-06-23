# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from aparnik.contrib.settings.models import Setting

User = get_user_model()


# Create your models here.
class InviteManager(models.Manager):

    def get_queryset(self):
        return super(InviteManager, self).get_queryset()

    def active(self):
        return self.get_queryset()

    def get_invited_by(self):
        return self.active()


class Invite(models.Model):

    invite = models.ForeignKey(User, related_name='invite', on_delete=models.CASCADE, verbose_name=_('Invite'))
    invited_by = models.ForeignKey(User, related_name='invite_by', on_delete=models.CASCADE, verbose_name=_('Invited By'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created At'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update At'))

    objects = InviteManager()

    def __str__(self):
        return '{}'.format(self.invite)

    class Meta:
        verbose_name = _('Invite')
        verbose_name_plural = _('Invites')

    def clean(self):
        # Don't allow complete action entries.
        if Invite.objects.filter(invite=self.invite).count() > 0:
            raise ValidationError({'invite': [_('This user invite before or invitation code is wrong.'), ]})

        if self.invited_by == self.invite:
            raise ValidationError({
                'invite': [_('Invite user can not be the same Invited user.'), ],
                'invited_by': [_('Invite user can not be the same Invited user.'), ]
                                   })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Invite, self).save(*args, **kwargs)


def post_save_invite_receiver(sender, instance, created, *args, **kwargs):

    if created:
        from aparnik.packages.shops.vouchers.models import Voucher
        # پس از قبول دعوت مبلغ بالا به حساب دعوت شده واریز می شود در صورتی که عدد مخالف صفر باشد.
        gift = round(Setting.objects.get(key='INVITED_GIFT_BON_CREDITS').get_value() / Setting.objects.get(
            key='APARNIK_BON_VALUE').get_value())
        if gift > 0:
            # کسی که دعوت شده
            user_obj = instance.invite
            Voucher.objects.add_voucher_by_admin_command(user_obj, gift, description='کاربر %s شما را دعوت کرده و شما دعوت او را پذیرفته اید و تعداد %s بن برای شما اعمال شد.'%(instance.invited_by, gift))

        gift = round(Setting.objects.get(key='INVITER_GIFT_BON_CREDITS').get_value() / Setting.objects.get(
            key='APARNIK_BON_VALUE').get_value())
        # پس از قبول دعوت مبلغ بالا به حساب دعوت کننده واریز می شود در صورتی که عدد مخالف صفر باشد.
        if gift > 0:
            # کسی که دعوت کرده
            user_obj = instance.invited_by
            Voucher.objects.add_voucher_by_admin_command(user_obj, gift,
                                                         description='کاربر %s دعوت شما را پذیرفت و تعداد %s بن برای شما اعمال شد.' % (
                                                         instance.invite, gift))


post_save.connect(post_save_invite_receiver, sender=Invite)
