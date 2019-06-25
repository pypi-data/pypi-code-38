from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AbstractDjangoSsoProfileModel(models.Model):
    """
    Abstract django-sso-app profile model
    """

    class Meta:
        abstract = True

    user = models.OneToOneField(User, related_name="profile",
                                on_delete="cascade")

    created_at = models.DateTimeField(auto_now_add=True)

    sso_id = models.CharField(max_length=36, unique=True, db_index=True)
    sso_rev = models.PositiveIntegerField()

    role = models.SmallIntegerField(null=True, blank=True)

    first_name = models.CharField(_('first name'), max_length=30, null=True,
                                  blank=True)
    last_name = models.CharField(_('last name'), max_length=30, null=True,
                                 blank=True)

    description = models.TextField(_('description'), null=True, blank=True)
    picture = models.TextField(_('picture'), null=True, blank=True)
    birthdate = models.DateField(_('birthdate'), null=True, blank=True)

    latitude = models.FloatField(_('latitude'), null=True, blank=True)
    longitude = models.FloatField(_('longitude'), null=True, blank=True)

    country = models.CharField(_('country'), max_length=46, null=True,
                               blank=True)

    address = models.TextField(_('address'), null=True, blank=True)
    language = models.CharField(_('language'), null=True, blank=True)

    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    language = models.CharField(max_length=3, null=True, blank=True)

    @property
    def username(self):
        return self.user.username

    @property
    def is_unsubscribed(self):
        return self.unsubscribed_at is not None

    @is_unsubscribed.setter
    def is_unsubscribed(self, value):
        self.unsubscribed_at = timezone.now()

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return self.user.username
