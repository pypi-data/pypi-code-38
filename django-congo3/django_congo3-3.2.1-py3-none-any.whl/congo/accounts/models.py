# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from congo.conf import settings
from congo.utils.validators import PHONE_REGEX


class AbstractGroup(Group):
    """
    Abstrakcyjna klasa grupy użytkowników służąca nadpisaniu panelu administracyjnego
    """

    class Meta:
        verbose_name = "Grupa użytkowników"
        verbose_name_plural = "Grupy użytkowników"
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

        email = self.normalize_email(email)
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
        """Metoda zwracająca użytkownika, który jest ustawiany jako wykonujący CRON-y"""

        if settings.CONGO_SYSTEM_USER_ID:
            return self.get(id = settings.CONGO_SYSTEM_USER_ID)
        return None


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    Abstrakcyjny model użytkownika
    """

    email = models.EmailField(_("Adres e-mail"), max_length = 255, unique = True)
    first_name = models.CharField(_("Imię"), max_length = 30, blank = True)
    last_name = models.CharField(_("Nazwisko"), max_length = 30, blank = True)
    mobile_phone = models.CharField(max_length = 25, validators = [PHONE_REGEX], blank = True, verbose_name = _("Telefon"), help_text = _("np. +48601123123"))
    is_staff = models.BooleanField(_("Czy w zespole"), default = False, help_text = _("Wyznacza czy użytkownik może zalogować się na tej stronie administratora."))
    is_active = models.BooleanField(_("Czy aktywny"), default = False, help_text = _("Wyznacza czy dany użytkownik powinien być traktowany jako aktywny. Odznacz to zamiast usuwania kont."))
    date_joined = models.DateTimeField(_("Data dołączenia"), default = timezone.now)

    objects = AbstractUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"
        abstract = True

        permissions = (
            ("run_migration", "Can run migration"),
        )

    def __str__(self):
        full_name = self.get_full_name()

        if full_name:
            return "%s (%s)" % (full_name, self.email)
        else:
            return self.email

    def get_full_name(self):
        return ("%s %s" % (self.first_name, self.last_name)).strip()

    get_full_name.short_description = _("Użytkownik")

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


class AbstractUserConfig(models.Model):
    """
    Abstrakcyjny model UserConfigu. Służy on do przechowywania wartości w kontekście użytkownika.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _("Użytkownik"), on_delete = models.CASCADE)
    name = models.SlugField(max_length = 80, verbose_name = _("Nazwa"))
    value = models.CharField(max_length = 255, verbose_name = _("Wartość"))

    class Meta:
        verbose_name = 'Parametr użytkownika'
        verbose_name_plural = 'Parametry użytkowników'
        unique_together = ('user', 'name')
        ordering = ('user', 'name')
        abstract = True

    def __str__(self):
        return "%s - %s: %s" % (self.user, self.name, self.value)

    @classmethod
    def get_value(cls, request, name, default_value = None):
        value = None
        if hasattr(request, 'session') and hasattr(request, 'user'):
            value = request.session.get(name)
            if value is None and request.user.is_authenticated:
                try:
                    value = cls.objects.filter(user = request.user, name = name).values_list('value', flat = True)[0]
                except IndexError:
                    pass
        return default_value if value is None else value

    @classmethod
    def set_value(cls, request, name, value):
        if hasattr(request, 'session') and hasattr(request, 'user'):
            if request.user.is_authenticated:
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
            if request.user.is_authenticated:
                cls.objects.filter(user = request.user, name = name).delete()
            if name in request.session:
                del request.session[name]


class AbstractUserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _("Użytkownik"), null = True, blank = True, on_delete = models.SET_NULL)
    date = models.DateTimeField(_("Data"), auto_now_add = True, db_index = True)
    content_type = models.ForeignKey(ContentType, verbose_name = _("Typ zawartości"), null = True, blank = True, on_delete = models.SET_NULL)
    object_id = models.PositiveIntegerField(_("ID obiektu"), null = True, blank = True)
    content_object = GenericForeignKey("content_type", "object_id")
    content_object.short_description = "Powiązany obiekt"

    parent_content_type = models.ForeignKey(ContentType, verbose_name = _("Typ zawartości rodzica"), related_name = "parent_content_type", null = True, blank = True, on_delete = models.CASCADE)
    parent_id = models.IntegerField(_("Id Rodzica"), blank = True, null = True)

    description = models.CharField(_("Opis"), max_length = 255, db_index = True)
    details = models.TextField(_("Szczegóły"), null = True, blank = True)
    http_referer = models.CharField(_("Adres odsyłający"), max_length = 255, blank = True, null = True)
    http_remote_addr = models.CharField(_("Adres IP"), max_length = 255, null = True, blank = True)
    http_user_agent = models.CharField(_("Aplikacja kliencka"), max_length = 255, null = True, blank = True)

    user_name = models.CharField(_("Imię i nazwisko"), max_length = 255, null = True, blank = True)
    object_name = models.CharField(_("Nazwa obiektu"), max_length = 255, null = True, blank = True)

    class Meta:
        verbose_name = _("Aktywność użytkownika")
        verbose_name_plural = _("Aktywności użytkowników")
        ordering = ('-date',)
        abstract = True

    def __str__(self):
        return "%s (%s, %s)" % (self.description, self.user, self.date)

    @classmethod
    def log(cls, request, content_object, description, original_object = None, details = None, parent_content_type = None, parent_id = None, **kwargs):
        """
        Metoda zapisuje aktywność użytkownika do logu. Pierwszym argumentem jest `request` (wymagane)
        Dalej podajemy `content_object`, czyli obiekt, którego bezpośrednio dotyczy zmiana, np. "karnet".
        Następnie podajemy `description`, tj. opis operacji, np. "Dodano karnet” lub "Zmieniono karnet".
        Następnie, jeśli podamy `original_object`, metoda wypisze zmiany między obiektem oryginalnym, a bieżącym, tj. `content_object`.
        Fakultatywnie możemy też podać `details`, czyli opis zmian (jako listę lub string).

        Jeśli jako argument kluczowy podamy `log_changes_only`, metoda dopisze rekord tylko wówczas, jeśli zaszły jakieś zmiany między `original_object` a `content_object`, albo jeśli podamy `details`.
        Operacja zostanie zapisana na konto użytkownika `request.user`, chyba, że jako argument kluczowy `user` podamy innego.
        W przypadku obiektów zawierających pola klasy `DateTimeField` trzeba pamiętać, że w opisie czasy zostaną zlokalizowane do strefy czasowej spotu. Aby ustawić inną strefę czasową, należy podać argument kluczowy `tz`.

        Przykład użycia dla dodawanego obiektu::

            details = translation.get_change_details()
            UserActivity.log(request, translation, _(u"Dodano opis Firmy"), details = details)

        Przykład użycia dla zmienianego obiektu::

            _original = copy(translation)
            # translation.description = description
            # translation.save()
            UserActivity.log(request, translation, _(u"Zmieniono opis Firmy"), _original, log_changes_only = True)

        Przykład użycia dla usuwanego obiektu::

            _original = copy(translation)
            # translation.delete()
            details = _original.get_change_details(reverse = True)
            UserActivity.log(request, _original, _(u"Usunięto opis Firmy"), details = details)
        """

        detail_list = []

        if isinstance(details, (list, tuple)):
            detail_list.extend(details)
        elif details:
            detail_list.append(details)

        if content_object and original_object and hasattr(content_object, 'get_change_details'):
            change_details_kwargs = {'tz': kwargs.get('tz', None)}
            detail_list.extend(content_object.get_change_details(original_object, **change_details_kwargs))

        if detail_list:
            details = "\n".join(detail_list) + "\n"
        else:
            details = None

        log_changes_only = kwargs.get('log_changes_only', False)
        if not details and log_changes_only:
            return

        if hasattr(request, 'user'):
            user = request.user
        else:
            user = None

        if 'user' in kwargs:
            user = kwargs['user']

        if not getattr(user, 'is_authenticated', False):
            user = None

        user_dict = {
            'user': user,
            'content_object': content_object,
            'description': description,
            'details': details,
            'parent_content_type': parent_content_type,
            'parent_id': parent_id,
        }

        if content_object:
            user_dict.update({'object_name': content_object})

        if hasattr(request, 'META'):
            user_dict['http_referer'] = request.META.get('HTTP_REFERER', None)
            user_dict['http_remote_addr'] = request.META.get('REMOTE_ADDR', None)
            user_dict['http_user_agent'] = request.META.get('HTTP_USER_AGENT', None)

        l = cls(**user_dict)
        l.save()
