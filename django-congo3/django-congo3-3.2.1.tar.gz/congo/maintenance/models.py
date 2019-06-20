# -*- coding: utf-8 -*-
from .managers import SiteManager
from congo.conf import settings
from congo.maintenance import SITE_CACHE
from congo.utils.managers import ActiveManager
from congo.utils.mixins import PositionMixin
from congo.utils.models import get_model
from django.core.cache import cache, caches
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _, pgettext
import copy
import importlib
import os
import re

class AbstractConfig(models.Model):
    """Abstrakcyjny model Configu. Służy do przechowywania zmiennych globalnych"""

    name = models.SlugField(_("Nazwa"), max_length = 255, unique = True)
    value = models.CharField(_("Wartość"), blank = True, max_length = 255)
    description = models.TextField(_("Opis"), null = True, blank = True, help_text = _("Fakultatywny opis parametru, w którym można wskazać cel jego przechowywania lub dozwolone wartości."))
    use_cache = models.BooleanField(_("Cachuj"), default = False, help_text = _("Czy zapisywać tę wartość w cache w celu poprawienia wydajności? Stosuj, gdy aktualność wartości nie jest priorytetowa."))
    load_at_startup = models.BooleanField(_("Wczytuj przy starcie"), default = False, help_text = _("Czy wczytywać wartość do cache’a przy starcie aplikacji? Stosuj, gdy parametr jest używany w kluczowych plikach aplikacji."))

    class Meta:
        verbose_name = _("Parametr systemu")
        verbose_name_plural = _("Parametry systemu")
        ordering = ('name',)
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def get_value(cls, name, default = None):
        cache = caches[settings.CONGO_CONFIG_CACHE_BACKEND]
        value = cache.get(name)

        if value is not None:
            return value

        try:
            config = cls.objects.get(name = name)
            if config.use_cache:
                cache.set(name, config.value)
            return config.value

        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, name, value):
        name = slugify(name)
        config, created = cls.objects.update_or_create(name = name, defaults = {'value': value})

        if config.use_cache:
            cache = caches[settings.CONGO_CONFIG_CACHE_BACKEND]
            cache.set(name, config.value)

    @classmethod
    def load_cache(cls):
        """
        Usage:
        
        class AppConfig(DjAppConfig):
            def ready(self):
                from maintenance.models import Config
                Config.load_cache()
        """

        cache = caches[settings.CONGO_CONFIG_CACHE_BACKEND]

        for name, value in cls.objects.filter(use_cache = True, load_at_startup = True).values_list('name', 'value'):
            cache.set(name, value)

    @classmethod
    def clear_cache(cls):
        cache = caches[settings.CONGO_CONFIG_CACHE_BACKEND]

        for name in cls.objects.filter(use_cache = True, load_at_startup = True).values_list('name', flat = True):
            cache.delete(name)

def clear_config_cache(sender, **kwargs):
    """
    Usage:
    
    from django.db.models.signals import pre_save, pre_delete
    pre_save.connect(clear_config_cache, sender = Config)
    pre_delete.connect(clear_config_cache, sender = Config)
    """

    instance = kwargs['instance']
    cache = caches[settings.CONGO_CONFIG_CACHE_BACKEND]
    cache.delete(instance.name)


class AbstractSite(models.Model):
    """Abstrakcyjny model Site. Używany jest gdy na jednej aplikacji uruchomione jest jednocześnie kilka stron"""

    domain = models.CharField(_("Domena"), max_length = 100)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, verbose_name = _("Język"))
    is_active = models.BooleanField(_("Aktywny"), default = False)

    objects = SiteManager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = _("Strona")
        verbose_name_plural = _("Strony")
        ordering = ('domain', 'is_active')
        abstract = True

    def __str__(self):
        return self.domain

def clear_site_cache(sender, **kwargs):
    instance = kwargs['instance']

    try:
        del SITE_CACHE[instance.pk]
    except KeyError:
        pass

# Usage
# from django.db.models.signals import pre_save, pre_delete
# pre_save.connect(clear_site_cache, sender = Site)
# pre_delete.connect(clear_site_cache, sender = Site)


class AbstractLog(models.Model):
    """Abstrakcyjny model Logów. Przechowują wszelkie informacje o błędach, wykonanych CRON-ach etc."""

    NOTSET = 0
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    LEVEL_CHOICE = (
        (NOTSET, 'NOTSET'),
        (DEBUG, 'DEBUG'),
        (INFO, 'INFO'),
        (SUCCESS, 'SUCCESS'),
        (WARNING, 'WARNING'),
        (ERROR, 'ERROR'),
        (CRITICAL, 'CRITICAL'),
    )

    name = models.CharField(_("Źródło"), max_length = 255, db_index = True)
    level = models.IntegerField(_("Poziom"), default = INFO, choices = LEVEL_CHOICE)
    message = models.CharField(_("Opis"), max_length = 255)
    user = models.CharField(_("Użytkownik"), max_length = 255, null = True, blank = True, db_index = True)
    date = models.DateTimeField(_("Data"), auto_now_add = True, db_index = True)
    args = models.TextField(_("Szczegóły"), null = True, blank = True)

    class Meta:
        verbose_name = _("Log systemowy")
        verbose_name_plural = _("Logi systemowe")
        ordering = ('-id',)
        abstract = True

    def __str__(self):
        return "%s: %s" % (self.get_level_name(self.level), self.name)

    @classmethod
    def is_valid_level(cls, level):
        level_dict = dict(cls.LEVEL_CHOICE)
        return level in list(level_dict.keys())

    @classmethod
    def get_level_name(cls, level):
        level_dict = dict(cls.LEVEL_CHOICE)
        return level_dict[level]

    @classmethod
    def get_max_level(cls, level_list, default = NOTSET):
        level = default
        for _level in level_list:
            if _level > level:
                level = _level
        return level

    @classmethod
    def render_level(cls, level):
        if level == cls.DEBUG:
            css_class = 'text-muted'
        elif level == cls.INFO:
            css_class = 'text-info'
        elif level == cls.SUCCESS:
            css_class = 'text-success'
        elif level == cls.WARNING:
            css_class = 'text-warning'
        elif level == cls.ERROR:
            css_class = 'text-danger'
        elif level == cls.CRITICAL:
            css_class = 'text-danger'
        else:
            css_class = ''
        label = cls.get_level_name(level)
        return mark_safe("""<span class="%s">%s</span>""" % (css_class, label))

def get_test_choice():
    """Metoda pozwalająca na dynamiczne dodawanie Audytów. Wystarczy wgrać plik z audytem do folderu CONGO_TEST_CHOICE_PATH"""
    test_choice_path = settings.CONGO_TEST_CHOICE_PATH
    if test_choice_path:
        return [(filename, filename) for filename in os.listdir(test_choice_path) if re.match("^(?!_)([a-z_]+).py$", filename, re.IGNORECASE)]
    return []


class AbstractAudit(models.Model):
    """Abstrakcyjny model Audytu. Audyty to testy sprawdzające stan systemu. Przykładowym testem jest np. maintenance.tests.unused_user_accounts"""

    TEST_CHOICE = get_test_choice()

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    LEVEL_CHOICE = (
        (DEBUG, 'DEBUG'),
        (INFO, 'INFO'),
        (WARNING, 'WARNING'),
        (ERROR, 'ERROR'),
        (CRITICAL, 'CRITICAL'),
    )

    EVERY_MINUTE = 10
    EVERY_HOUR = 20
    EVERY_DAY = 30
    EVERY_WEEK = 40
    EVERY_MONTH = 50

    FREQUENCY_CHOICE = (
        (EVERY_MINUTE, _("Co minutę")),# eg. every min
        (EVERY_HOUR, _("Co godzinę")),
        (EVERY_DAY, _("Co dzień")),
        (EVERY_WEEK, _("Co tydzień")),
        (EVERY_MONTH, _("Every month")),
    )

    test = models.CharField(_("Test"), max_length = 255, unique = True, choices = TEST_CHOICE)
    level = models.IntegerField(_("Poziom"), default = INFO, choices = LEVEL_CHOICE)
    frequency = models.IntegerField(_("Częstotliwość"), choices = FREQUENCY_CHOICE)
    is_active = models.BooleanField(_("Aktywny"), default = False)
    last_run_date = models.DateTimeField(_("Ostatnie uruchomienie"), null = True, blank = True)
    result = models.NullBooleanField(_("Wynik"), default = None)
    details = models.TextField(_("Szczegóły"), null = True, blank = True)
    auditors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank = True, limit_choices_to = {'is_staff': True}, related_name = 'user_audits', verbose_name = _("Audytorzy"))

    class Meta:
        verbose_name = _("Audyt systemu")
        verbose_name_plural = _("Audyty systemu")
        ordering = ('test',)
        permissions = (
            ("run_test", "Can run audit test"),
        )
        abstract = True

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.test[:-3]

    def _get_test(self):
        tests_module = settings.CONGO_TESTS_MODULE
        if not tests_module:
            raise ImproperlyConfigured("In order to use Audit model, configure settings.CONGO_TESTS_MODULE first.")

        if self.test:
            module_path = "%s.%s" % (tests_module, self.name)
            module = importlib.import_module(module_path)
            return module.Test()

        return None

    def run_test(self, user):
        test = self._get_test()
        success, result = test.run(user)

        self.last_run_date = timezone.now()
        self.result = result['result']
        self.details = result['details']
        self.save(update_fields = ('last_run_date', 'result', 'details'))

        return success

def get_job_choice():
    """Metoda pozwalająca na dynamicznie dodawanie nowych CRON-ów. Wystarczy wgrać plik z audytem do folderu CONGO_JOB_CHOICE_PATH"""

    job_choice_path = settings.CONGO_JOB_CHOICE_PATH
    if job_choice_path:
        return [(filename, filename) for filename in os.listdir(job_choice_path) if re.match("^(?!_)([a-z_]+).py$", filename, re.IGNORECASE)]
    return []


class AbstractCron(PositionMixin):
    """Abstrakcyjny model CRON. CRON-y to uruchamiane regularnie zadania, np. czyszczenie logów"""

    JOB_CHOICE = get_job_choice()

    EVERY_MINUTE = 10
    EVERY_THREE_MINUTES = 11
    EVERY_TEN_MINUTES = 12

    EVERY_HOUR = 20
    WORKING_HOURS = 21
    MORNINGS_EVENINGS = 22
    AFTER_HOURS = 23

    EVERY_DAY = 30
    EVERY_DAY_AT_NOON = 35
    EVERY_WEEK = 40
    EVERY_MONTH = 50

    FREQUENCY_CHOICE = (
        (EVERY_MINUTE, _("Co minutę")),# eg. every min
        (EVERY_THREE_MINUTES, _("Co trzy minuty")),# eg. every 3 min
        (EVERY_TEN_MINUTES, _("Co 10 minut")),# eg. every 10 min

        (EVERY_HOUR, _("Co godzinę")),# eg. 5 past hour
        (WORKING_HOURS, _("W godzinach pracy")),# eg. every 5 min from 8 am to 7 pm mon to sat
        (MORNINGS_EVENINGS, _("Rano i wieczorem")),# eg. 7:55 am and 7:55 pm
        (AFTER_HOURS, _("Po godzinach")),# eg. every 3 min from 5 pm to 9 pm mon to sat

        (EVERY_DAY, _("Co dzień")),# eg. 10 past midnight
        (EVERY_DAY_AT_NOON, _("Co dzień w południe")),# eg. 10 past noon
        (EVERY_WEEK, _("Co tydzień")),# eg. 15 past midnight on mon
        (EVERY_MONTH, _("Co miesiąc")),# eg. 20 past midnight on 1-st month day
    )

    job = models.CharField(_("Zadanie"), max_length = 255, unique = True, choices = JOB_CHOICE)
    frequency = models.IntegerField(_("Częstotliwość"), choices = FREQUENCY_CHOICE)
    is_active = models.BooleanField(_("Aktywny"), default = False)
    last_run_date = models.DateTimeField(_("Ostatnie uruchomienie"), null = True, blank = True)

    class Meta:
        verbose_name = _("Zadanie CRON")
        verbose_name_plural = _("Zadania CRON")
        ordering = ("position",)
        permissions = (
            ("run_job", "Can run CRON job"),
        )
        abstract = True

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.job[:-3]

    def _get_job(self):
        jobs_module = settings.CONGO_JOBS_MODULE
        if not jobs_module:
            raise ImproperlyConfigured("In order to use Cron model, configure settings.CONGO_JOBS_MODULE first.")

        if self.job:
            module_path = "%s.%s" % (jobs_module, self.name)
            module = importlib.import_module(module_path)
            return module.Job()

        return None

    def run_job(self, user):
        job = self._get_job()
        success = job.run(user)

        self.last_run_date = timezone.now()
        self.save(update_fields = ['last_run_date'])

        return success


class AbstractUrlRedirect(models.Model):
    """Abstrakcyjny model przekierowań URL"""

    old_url = models.CharField(_("Stary URL"), max_length = 255, db_index = True, help_text = _("Format: ^/old-url/$"))
    redirect_url = models.CharField(_("Nowy URL"), max_length = 255, help_text = _("Format: /new-url/"))
    rewrite_tail = models.BooleanField(_("Przepisać ogon"), default = False, help_text = _("Czy zamienić /old-url/abc/ na /new-url/abc/ czy jedynie /new-url/?"))
    is_permanent_redirect = models.BooleanField(_("Permanentne przekierowanie?"), default = True, help_text = _("Czy przekierowanie jest permanentne (301) czy tymczasowe (302)?"))

    class Meta:
        verbose_name = _("Przekierowanie URL")
        verbose_name_plural = _("Przekierowania URL")
        ordering = ('old_url',)
        abstract = True

    def __str__(self):
        return "%s > %s" % (self.old_url, self.redirect_url)

    @classmethod
    def _get_query(cls):
        db_table = cls.objects.model._meta.db_table
        query = """
            SELECT *
            FROM %s
            WHERE $s REGEXP old_url
            ORDER BY LENGTH(old_url) - LENGTH(REPLACE(old_url, '/', '')) DESC
            LIMIT 1
        """ % db_table
        query = query.replace('$s', '%s')
        return query

    @classmethod
    def get_redirect_tuple(cls, old_url):
        query = cls._get_query()

        if not old_url.endswith('/') and not '?' in old_url:
            old_url += "/"

        try:
            redirect = list(cls.objects.raw(query, [old_url]))[0]

            if settings.DEBUG:
                print
                print("%s > %s" % (redirect.old_url, redirect.redirect_url))
                print("  rewrite_tail: %s, is_permanent_redirect %s" % (redirect.rewrite_tail, redirect.is_permanent_redirect))
                print

            if redirect.rewrite_tail:
                redirect_url = old_url.replace(redirect.old_url.replace('^', '').replace('$', ''), redirect.redirect_url)
            else:
                redirect_url = redirect.redirect_url

            return (redirect_url, redirect.is_permanent_redirect)
        except IndexError:

            return (None, None)


class AbstractHoliday(models.Model):
    """Abstrakcyjny model wolnego. Pokazuje dni wolne od pracy i dni pracujące"""

    date = models.DateField(db_index = True, verbose_name = _("Data"))
    description = models.CharField(max_length = 255, blank = True, verbose_name = _("Opis"))
    is_working_day = models.BooleanField(default = False, verbose_name = _("Czy dzień pracujący"))

    class Meta:
        verbose_name = _("Dzień świąteczny")
        verbose_name_plural = "Dni świąteczne"
        ordering = ('-date',)
        abstract = True

    def __str__(self):
        if self.description:
            return "%s (%s)" % (self.description, self.date)
        else:
            return "%s" % self.date

    @classmethod
    def get_opening_hours(cls, date = None):
        _config_model = get_model('CONGO_CONFIG_MODEL')

        opening_hours = []
        opening_hours_config = _config_model.get_value('opening_hours', '').split(';')

        for hours in opening_hours_config:
            if hours:
                opening_hours.append(hours.split(','))

        return opening_hours

    @classmethod
    def get_opening_hours_for_week(cls):
        periods = [pgettext('weekday', "Pn. - Pt."), pgettext('weekday', "Sb."), pgettext('weekday', "Nd.")]
        opening_hours = cls.get_opening_hours()
        opening_hours_for_week = []

        for i in range(len(periods)):
            try:
                if len(opening_hours[i]):
                    opening_hours_for_week.append([periods[i], " - ".join(opening_hours[i])])
            except IndexError:
                pass
        return opening_hours_for_week

    @classmethod
    def get_opening_hours_for_today(cls):
        opening_hours = cls.get_opening_hours()
        now = timezone.localtime(timezone.now())
#        now = datetime.datetime(2015, 4, 12, 14, 1)
        weekday = now.weekday()
        period = weekday - 4 if weekday > 4 else 0
        is_open = False

        try:
            todays_hours = opening_hours[period]
        except IndexError:
            todays_hours = None

        if todays_hours:
            if cls.objects.filter(date = now, is_working_day = False).exists():
                todays_hours = None
                is_open = False
            else:
                open_hour_list = todays_hours[0].split(':')
                open_hour = copy.copy(now).replace(hour = int(open_hour_list[0]), minute = int(open_hour_list[1]), second = 0)
                close_hour_list = todays_hours[1].split(':')
                close_hour = copy.copy(now).replace(hour = int(close_hour_list[0]), minute = int(close_hour_list[1]), second = 0)
                is_open = now >= open_hour and now <= close_hour

        return (todays_hours, is_open)

class AbstractTrustedIPAddress(models.Model):
    ip_address = models.GenericIPAddressField(_("Adres IP"))
    description = models.CharField(_("Opis"), max_length = 255)
    is_active = models.BooleanField(_("Aktywna"), default = False)
    add_date = models.DateTimeField("Data dodania", auto_now_add = True)
    change_date = models.DateTimeField("Data zmiany", auto_now = True)

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = _("Zaufany adres IP")
        verbose_name_plural = _("Zaufne adresy IP")
        abstract = True

    def __str__(self):
        return "Adres IP: %s" % self.ip_address

    @classmethod
    def get_from_cache(cls):
        key = "trusted_ip_address_list"
        cache = caches[settings.TRUSTED_IP_CACHE_BACKEND]
        ip_list = cache.get(key)

        if ip_list is None:
            ip_list = cls.active_objects.all().values_list('ip_address', flat = True)
            cache.set(key, ip_list)

        return ip_list