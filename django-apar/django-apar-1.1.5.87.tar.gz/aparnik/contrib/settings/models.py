# -*- coding: utf-8 -*-


import string
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.utils.timezone import now
from django.conf import settings


# Create your models here.
class SettingManager(models.Manager):

    def get_queryset(self):
        return super(SettingManager, self).get_queryset()

    def active(self):
        return self.get_queryset()

    def home_properties(self):
        return self.active().filter(is_variable_in_home=True)


class Setting(models.Model):
    STRING_VALUE = 's'
    INT_VALUE = 'i'
    BOOL_VALUE = 'b'
    DATATIME_VALUE = 'dt'
    FUNCTION_SETTING_RETURN_VALUE = 'fr'
    VALUE_TYPE = (
        (STRING_VALUE, _('String')),
        (INT_VALUE, _('Int')),
        (BOOL_VALUE, _('Boolean')),
        (DATATIME_VALUE, _('Date Time')),
        (FUNCTION_SETTING_RETURN_VALUE, _('Function setting return value'))
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    key = models.CharField(max_length=255, verbose_name=_('Key'))
    value = models.TextField(verbose_name=_('Value'))
    value_type = models.CharField(max_length=31, verbose_name=_('Value Type'), choices=VALUE_TYPE)
    package_name = models.CharField(max_length=70, verbose_name=_('Package name'), null=True, blank=True)
    function_name = models.CharField(max_length=70, verbose_name=_('Function name'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_show = models.BooleanField(default=True, verbose_name=_('Is Show'))
    is_variable_in_home = models.BooleanField(default=False, verbose_name=_('Is variable show in home'))

    objects = SettingManager()

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Setting, self).__init__(*args, **kwargs)

    def get_value(self):
        if self.value_type == self.INT_VALUE:
            return int(self.value)
        elif self.value_type == self.STRING_VALUE:
            return self.value
        elif self.value_type == self.BOOL_VALUE:
            return self.value == 'True'
        elif self.value_type == self.DATATIME_VALUE:
            # TODO: fix it
            return now()
        elif self.value_type == self.FUNCTION_SETTING_RETURN_VALUE:
            return getattr(settings, self.value)

    def clean(self):
        invalid_chars = ' ?!@#$%^&*()+=-'
        for letter in invalid_chars:
            if letter in str(self.key):
                raise ValidationError({'key': [_('INVALID KEY')]})

        from string import digits
        if str(self.key[0]) in digits:
            raise ValidationError(
                {'key': [_('first char of key must be lowercase letter or uppercase letter or underscore !')]}
            )

        if self.value_type == self.INT_VALUE:
            try:
                int(self.value)
            except:
                raise ValidationError({'value': [_('This field is Mismatch')]})
        elif self.value_type == self.BOOL_VALUE:
            ok = True
            if not (self.value == 'True' or self.value == 'False'):
                ok = False

            if not ok:
                raise ValidationError({'value': [_('This field is Mismatch')]})
        elif self.value_type == self.STRING_VALUE:
            ok = True
            # for letter in str(self.value):
            #     if (letter not in string.lowercase) and (letter not in string.uppercase):
            #         ok = False
            #         break
            # if not ok:
            #     raise ValidationError({'value': [_('This field is Mismatch')]})
        elif self.value_type == self.DATATIME_VALUE:
            # TODO: support this type
            raise ValidationError({'value': [_('This field is Mismatch')]})
        elif self.value_type == self.FUNCTION_SETTING_RETURN_VALUE:
            try:
                getattr(settings, self.value)
            except Exception:
                raise ValidationError({'value': [_('The key does not exists in settings.')]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Setting, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('setting')
        verbose_name_plural = _('settings')


def post_save_settings_receiver(sender, instance, created, *args, **kwargs):

    if instance.package_name is not None and instance.function_name is not None:
        Klass = import_string(instance.package_name)
        func = getattr(Klass, instance.function_name)
        func(instance.value, instance.value_type)


post_save.connect(post_save_settings_receiver, sender=Setting)
