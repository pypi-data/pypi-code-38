# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from django.core.validators import RegexValidator, ValidationError, MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from django_enumfield import enum

from aparnik.settings import aparnik_settings, Setting
from aparnik.utils.formattings import formatprice
from aparnik.utils.fields import PhoneField, NationalCodeField, PriceField

from aparnik.contrib.province.models import City

import uuid
from kavenegar import *


class UserManager(BaseUserManager):
    # use_in_migrations = True
    def get_queryset(self):
        return super(UserManager, self).get_queryset()

    def active(self):
        return self.get_queryset()

    # python manage.py createsuperuser
    def create_superuser(self, username, first_name, last_name, is_staff=None, password=None):

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            sex=User.SEX_MALE,
            is_staff=True,
            is_active=True,
            is_superuser=True
        )
        user.save()
        return user

    def admins(self):
        return self.active().filter(groups__id__in=[1])


# PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    SEX_MALE = 'M' # TYPE_INT = 0
    SEX_WOMAN = 'F'
    SEX_TYPE = (
        (SEX_MALE, "مرد"),
        (SEX_WOMAN, "زن")
    )
    sys_id = models.AutoField(primary_key=True, blank=True, verbose_name=_('System ID'))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_('UUID'))
    password = None
    passwd = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Password'))
    username = PhoneField(max_length=30, mobile=True, unique=True, verbose_name=_('Mobile'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('Email'))
    first_name = models.CharField(max_length=12, null=True, blank=True, verbose_name=_('Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Family'))
    username_mention = models.CharField(default='a', max_length=100, unique=True, validators=[RegexValidator(
            regex='^[a-zA-Z_\-0-9]+$',
            message='Username must be Alphanumeric',
            code='invalid_username'
        ),], verbose_name=_('Username for mention'))
    sex = models.CharField(max_length=1, choices=SEX_TYPE, default='M', verbose_name=_('Sex'))
    avatar = models.ForeignKey('filefields.FileField', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Avatar'))
    current_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Current City'))
    birthdate = models.DateTimeField(blank=True, null=True, verbose_name=_('Birthdate'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is Staff'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    token = models.CharField(blank=True, null=True, max_length=4, verbose_name=_('Token'))
    token_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Token Time'))
    limit_device_login = models.IntegerField(default=-1, help_text=_('If the number is set to -1, then the value in the settings will apply'), verbose_name=_('Limit device login'))
    invitation_code = models.CharField(editable=False, null=True, blank=True, max_length=36, verbose_name=_('Invitation Code'))
    verify_mobile = models.BooleanField(default=False, verbose_name=_('Verify Mobile'))
    wallet = PriceField(big=True, default=0, verbose_name=_('Wallet'))
    co_sale_percentage_value = models.IntegerField(default=-1, validators=[MaxValueValidator(100), MinValueValidator(-1)], help_text=_('If the number is set to -1, then the value in the settings will apply'), verbose_name=_('Co Sale Percentage'))
    company_national_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Company national number'))
    company_registration_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Company registeration number'))
    company_economical_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Company economical number'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = UserManager()

    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS must contain all required fields on your User model,
    # but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_staff']

    class Meta:
        app_label = 'aparnik_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __unicode__(self):
        return '%s %s' % (self.username, self.get_full_name())

    def clean(self):
        if aparnik_settings.USER_LOGIN_WITH_PASSWORD and self.passwd == '':
            raise ValidationError({'passwd': [_('Required password, Please Disabel USER_LOGIN_WITH_PASSWORD')]})

        if self.username_mention == 'a':
            from faker import Faker
            faker = Faker()
            username = faker.user_name()
            while User.objects.filter(username_mention=username).exists():
                username = faker.user_name()
            self.username_mention = username

    def save(self, *args, **kwargs):

        def generate():
            base = 4
            invitation_code = uuid.uuid4()

            if aparnik_settings.USER_INVITATION_CODE_INT:

                invitation_code = invitation_code.int
            else:
                invitation_code = invitation_code.__str__().replace('-', '')

            invitation_code = invitation_code[base:base + aparnik_settings.USER_INVITATION_CODE_LENGTH]
            if User.objects.filter(invitation_code=invitation_code).count() > 0:
                return generate()
            return invitation_code

        if self.invitation_code is None:
            self.invitation_code = generate()

        self.full_clean()
        return super(User, self).save(*args, **kwargs)

    def get_api_uri(self):
        return reverse("aparnik-api:users:detail", kwargs={"username": self.username})

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def device_login_count(self):
        return self.devicelogin_set.get_login_count(user=self)

    def is_can_login(self, device_id=None):

        limit_device_login = self.limit_device_login if self.limit_device_login >= 0 else Setting.objects.get(key='USER_DEFAULT_LIMIT_DEVICE_LOGIN').get_value()

        if Setting.objects.get(key='USER_IS_LIMIT_DEVICE_LOGIN_ACTIVE').get_value():

            if device_id and self.devicelogin_set.active().filter(device_id=device_id).exists():
                return True

            if device_id and Setting.objects.get(key='USER_IS_LIMIT_DEVICE_LOGIN_ACTIVE').get_value() and self.devicelogin_set.get_login_count(user=self) >= limit_device_login :
                raise ValidationError(_('تعداد دستگاه های فعال شما بیش از %(value)s است.'), params={'value': limit_device_login})

        return True

    def reset_password(self):
        passwd = str(uuid.uuid4().int)[:5]

        if aparnik_settings.VERIFY_FAKE:

            passwd = aparnik_settings.VERIFY_FAKE_CODE

        self.passwd = passwd
        self.save()

        if aparnik_settings.SEND_SMS:
            try:
                api = KavenegarAPI(aparnik_settings.SMS_API_KEY)
                params = {
                    'receptor': self.username,
                    'template': aparnik_settings.SMS_OTA_NAME,
                    'token': self.first_name.replace(' ', '-') if self.first_name is not None else 'مهمان',
                    'token2': self.passwd,
                    'type': 'sms',  # sms vs call
                }
                response = api.verify_lookup(params)
                # print(response)

            except APIException as e:
                print(e)

            except HTTPException as e:
                print(e)

    def OTAVerify(self, token):

        if aparnik_settings.VERIFY_FAKE:

            if token == aparnik_settings.VERIFY_FAKE_CODE:
                self.token = None
                self.token_time = None
                return True

        if self.token is None:
            return False

        diff = (now() - self.token_time).total_seconds()

        if (diff < aparnik_settings.SMS_EXPIRE_TOKEN and diff > 0 ) and self.token == token:

            self.token = None
            self.token_time = None
            self.save()
            return True

        return False

    def OTARequest(self, app_signature=None):

        if self.token_time and (now() - self.token_time).total_seconds() < int(aparnik_settings.SMS_EXPIRE_TOKEN):
            # raise ValidationError({'username': [_('Verification code sent before. Please wait until code expired.')]})
            return

        self.token = str(uuid.uuid4().int)[-4:]
        self.token_time = now()
        self.save()

        if aparnik_settings.SEND_SMS:
            try:
                if not app_signature:
                    app_signature = 'Code:%s' % self.token

                api = KavenegarAPI(aparnik_settings.SMS_API_KEY)
                params = {
                    'receptor': self.username,
                    'template': aparnik_settings.SMS_OTA_NAME,
                    'token': self.token, #self.first_name.replace(' ', '-') if self.first_name is not None else 'مهمان',
                    'token2': app_signature,
                    'type': 'sms',  # sms vs call
                }
                response = api.verify_lookup(params)
                # print(response)

            except APIException as e:
                print(e)

            except HTTPException as e:
                print(e)

    # # this methods are require to login super user from admin panel
    # def has_perm(self, perm, obj=None):
    #     return self.is_staff
    #
    # # this methods are require to login super user from admin panel
    # def has_module_perms(self, app_label):
    #     return self.is_staff
    @property
    def is_new_registered(self):
        new_register = (not self.first_name) or (not self.last_name)
        if aparnik_settings.USER_LOGIN_WITH_PASSWORD:
            new_register = new_register or not self.verify_mobile
        return new_register

    @property
    def wallet_string(self):
        return '%s' % formatprice.format_price(self.wallet)

    @property
    def is_admin(self):
        return self.groups.filter(name='admin').exists() or self.is_superuser

    @property
    def co_sale_percentage(self):
        if self.co_sale_percentage_value == -1:
            from aparnik.settings import Setting
            inviter_per_purchase_value = Setting.objects.get(key='INVITER_GIFT_CREDITS_PER_PURCHASE').get_value()
            return inviter_per_purchase_value
        return self.co_sale_percentage_value

    @property
    def co_sale_summary(self):
        from aparnik.packages.shops.cosales.models import CoSale
        return CoSale.objects.summary(user=self)

    # دعوت شده توسط
    @property
    def invited_by(self):
        invited_by = self.invite.first()
        if invited_by:
            return invited_by.invited_by
        return None


def post_save_user_receiver(sender, instance, created, *args, **kwargs):

    if created and instance.is_new_registered:
        instance.OTARequest()


post_save.connect(post_save_user_receiver, sender=User)


class DeviceLoginManager(models.Manager):

    def get_queryset(self):
        return super(DeviceLoginManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def get_login(self, user):
        return self.active().filter(user=user).values_list('device_id', flat=True).distinct()

    def get_login_count(self, user):
        return self.get_login(user=user).count()


# Create your models here.
class DeviceType(enum.Enum):
    ANDROID = 0
    IOS = 1
    WEB = 2

    labels = {
        ANDROID: _('Android'),
        IOS: _('iOS'),
        WEB: _('Web')
    }

    @staticmethod
    def find(value):
        switcher = {
            'a': DeviceType.ANDROID,
            'i': DeviceType.IOS,
            'w': DeviceType.WEB
        }

        return switcher.get(value, None)

    @staticmethod
    def value(value):
        switcher = {
            DeviceType.ANDROID: 'android',
            DeviceType.IOS: 'ios',
            DeviceType.WEB: 'web',
        }

        return switcher.get(value, None)


class DeviceLogin(models.Model):

    user = models.ForeignKey('aparnik_users.User', on_delete=models.CASCADE, verbose_name=_('User'))
    version_number = models.FloatField(verbose_name=_('Version Number'))
    device_id = models.CharField(max_length=255, verbose_name=_('Device Id'))
    os_version = models.CharField(max_length=255, verbose_name=_('OS Version'))
    device_model = models.CharField(max_length=255, verbose_name=_('Device Model'))
    device_type = enum.EnumField(DeviceType, default=DeviceType.ANDROID, verbose_name=_('Device Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = DeviceLoginManager()

    def __unicode__(self):
        return self.device_id

    class Meta:
        verbose_name = _('Device Login')
        verbose_name_plural = _('Devices Login')
