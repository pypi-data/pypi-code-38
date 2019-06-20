# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.validators import PHONE_REGEX
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

class AbstractGroup(Group):
    """
    Abstrakcyjna klasa grupy użytkowników
    """

    class Meta:
        verbose_name = u"Grupa użytkowników"
        verbose_name_plural = u"Grupy użytkowników"
        abstract = True

class AbstractUserManager(BaseUserManager):
    """
    Abstrakcyjny manager użytkowników
    """

    def create_user(self, email, password = None, **extra_fields):
        """Metoda służąca do tworzenia nowych użytkowników. Każda akcja tworzenia nowego użytkownika, powinna być obsługiwana przez tę funkcję"""

        # for python-social-auth
        if 'username' in extra_fields:
            del extra_fields['username']

        now = timezone.now()

        if not email:
            raise ValueError("Users must have an email address")
        email = AbstractUserManager.normalize_email(email)
        user = self.model(email = email, is_staff = False, is_active = True, is_superuser = False, last_login = now, date_joined = now, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Metoda służąca do tworzenia nowych super-użytkowników. Każda akcja tworzenia nowego użytkownika, powinna być obsługiwana przez tę funkcję"""

        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

    def get_system_user(self):
        """Metoda zwracająca użytkownika, który jest ustawiany jako wykonywującego CRON-y"""

        return self.get(id = settings.SYSTEM_USER_ID)

@python_2_unicode_compatible
class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """Abstrakcyjny model użytkownika"""

    email = models.EmailField(_(u"Adres e-mail"), max_length = 255, unique = True)
    first_name = models.CharField(_(u"Imię"), max_length = 30, blank = True)
    last_name = models.CharField(_(u"Nazwisko"), max_length = 30, blank = True)
    mobile_phone = models.CharField(max_length = 25, validators = [PHONE_REGEX], blank = True, verbose_name = _(u"Telefon"), help_text = _(u"np. +48601123123"))
    is_staff = models.BooleanField(_(u"Staff status"), default = False, help_text = _(u"Wyznacza czy użytkownik może zalogować się na tej stronie administratora."))
    is_active = models.BooleanField(_(u"Aktywny"), default = True, help_text = _(u"Wyznacza czy dany użytkownik powinien być traktowany jako aktywny. Odznacz to zamiast usuwania kont."))
    date_joined = models.DateTimeField(_(u"Data dołączenia"), default = timezone.now)

    objects = AbstractUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = u"Użytkownik"
        verbose_name_plural = u"Użytkownicy"
        abstract = True

        permissions = (
            ("run_migration", "Can run migration"),
        )

    def __init__(self, *args, **kwargs):
        super(AbstractUser, self).__init__(*args, **kwargs)

    def __str__(self):
        full_name = self.get_full_name()

        if full_name:
            return u"%s (%s)" % (full_name, self.email)
        else:
            return self.email

    def get_full_name(self):
        return (u"%s %s" % (self.first_name, self.last_name)).strip()
    get_full_name.short_description = _(u"Użytkownik")

    def get_short_name(self):
        if self.first_name or self.last_name:
            return self.first_name or self.last_name
        else:
            return self.email

    def get_full_name_or_email(self):
        full_name = self.get_full_name()

        if full_name:
            return full_name
        else:
            return self.email

@python_2_unicode_compatible
class AbstractUserConfig(models.Model):
    """Abstrakcyjny model UserConfigu. Służy on do przechowywania wartości w kontekście użytkownika"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _(u"Użytkownik"))
    name = models.SlugField(max_length = 30, verbose_name = _(u"Nazwa"))
    value = models.CharField(max_length = 255, verbose_name = _(u"Wartość"))

    class Meta:
        verbose_name = u'Parametr użytkownika'
        verbose_name_plural = u'Parametry użytkowników'
        unique_together = ('user', 'name')
        ordering = ('user', 'name')
        abstract = True

    def __str__(self):
        return u"%s - %s: %s" % (self.user, self.name, self.value)

    @classmethod
    def get_value(cls, request, name, default_value = None):
        value = None
        if hasattr(request, 'session') and hasattr(request, 'user'):
            value = request.session.get(name)
            if value is None and request.user.is_authenticated():
                try:
                    value = cls.objects.filter(user = request.user, name = name).values_list('value', flat = True)[0]
                except IndexError:
                    pass
        return default_value if value is None else value

    @classmethod
    def set_value(cls, request, name, value):
        if hasattr(request, 'session') and hasattr(request, 'user'):
            if request.user.is_authenticated():
                try:
                    config = cls.objects.get(user = request.user, name = name)
                    config.value = value
                    config.save(update_fields = ['value'])
                except cls.DoesNotExist:
                    config = cls(user = request.user, name = name, value = value)
                    config.save(force_insert = True)
            request.session[name] = value

    @classmethod
    def delete_value(cls, request, name):
        if hasattr(request, 'session') and hasattr(request, 'user'):
            if request.user.is_authenticated():
                cls.objects.filter(user = request.user, name = name).delete()
            if name in request.session:
                del request.session[name]
