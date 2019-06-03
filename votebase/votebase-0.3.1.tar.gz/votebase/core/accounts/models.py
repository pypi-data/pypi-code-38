import hashlib
import random

from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext, ugettext_lazy as _

from votebase.core.accounts.helpers import get_user_profile, create_user_profile


class User(AbstractUser):
    class Meta:
        app_label = 'accounts'
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('user')

    def get_profile(self):
        profile = get_user_profile(self)

        if not profile:
            return create_user_profile(self)

        return profile


class Profile(models.Model):
    PACKAGE_BASIC = 'BASIC'
    PACKAGE_STANDARD = 'STANDARD'
    PACKAGE_PREMIUM = 'PREMIUM'
    PACKAGES = (
        (PACKAGE_BASIC, _(u'Basic')),
        (PACKAGE_STANDARD, _(u'Standard')),
        (PACKAGE_PREMIUM, _(u'Premium')),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, verbose_name=_(u'user'))
    _package = models.CharField(_(u'package'), db_column='package', max_length=32, choices=PACKAGES,
        blank=False, null=False, default=PACKAGE_BASIC)
    package_valid_to = models.DateTimeField(_(u'package valid to'), default=now)
    activation_hash = models.CharField(_(u'activation hash'), max_length=255,
        blank=True, null=True, default=None)
    api_key = models.CharField(_(u'API key'), max_length=255,
        blank=True, null=True, default=None)
    slug = models.SlugField(_(u'URL alias'), max_length=60, unique=True)
    first_name = models.CharField(
        _(u'first name'), default=None, blank=True, null=True, max_length=30)
    last_name = models.CharField(
        _(u'last name'), default=None, blank=True, null=True, max_length=30)
    last_seen_surveys = models.DateTimeField(
        _(u'last seen surveys'), default=now)

    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(
        ('m', 'Male'), ('f', 'Female')), blank=True, null=True)

    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))

    class Meta:
        app_label = 'accounts'
        db_table = 'votebase_profiles'
        verbose_name = _(u'profile')
        verbose_name_plural = _(u'profiles')
        ordering = ('-created', )

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self._meta.get_field('date_of_birth').verbose_name = ugettext(u'date of birth')

    def __unicode__(self):
        return self.get_full_name()

    @models.permalink
    def get_absolute_url(self):
        if self.slug is None or self.slug == '':
            return 'users_pk', (str(self.pk), )
        return 'users_slug', (self.slug, )

    def get_gender_real_display(self):
        if self.gender == 'm':
            return ugettext(u'Male')
        if self.gender == 'f':
            return ugettext(u'Female')
        return ugettext(u'None')

    def get_full_name(self):
        if (self.first_name is None or self.first_name.strip() in EMPTY_VALUES) and\
            (self.last_name is None or self.last_name.strip() in EMPTY_VALUES):
            return self.user.username
        return u'%s %s' % (self.first_name, self.last_name)

    def is_valid(self):
        return now() <= self.package_valid_to

    @property
    def hash(self):
        return self.activation_hash

    # Important !!!
    # Return free (BASIC) package if not valid
    @property
    def package(self):
        return self._package if self.is_valid() else Profile.PACKAGE_BASIC

    def get_package_display(self):
        p = self.package
        return force_unicode(dict(Profile.PACKAGES).get(p, p), strings_only=True)

    def get_monthly_fee(self):
        return settings.VOTEBASE_PACKAGES_SETTINGS[self.package]['monthly_fee']

    def get_voters_limit(self):
        return settings.VOTEBASE_PACKAGES_SETTINGS[self.package]['voters_limit']

    def is_permitted_to_create_segment(self):
        return not self.package == Profile.PACKAGE_BASIC

    def is_permitted_to_enter_branding(self):
        return self.package == Profile.PACKAGE_PREMIUM

    def save(self, *args, **kwargs):
        self.modified = now()
        super(Profile, self).save(*args, **kwargs)

        if self.activation_hash in EMPTY_VALUES:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_hash = hashlib.sha1(salt + unicode(self.user.username)).hexdigest()
            self.activation_hash = activation_hash
            self.save()

        if self.api_key in EMPTY_VALUES:
            api_key = None
            while api_key is None:
                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                hash = hashlib.sha1(salt + self.user.username).hexdigest()[:16]
                if not Profile.objects.filter(api_key=hash).exists():
                    api_key = hash
            self.api_key = api_key
            self.save()
