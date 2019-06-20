# -*- coding: utf-8 -*-
from .managers import SiteManager
from congo.conf import settings
from congo.maintenance import SITE_CACHE, CONFIG_CACHE
from congo.utils.managers import ActiveManager
from congo.utils.mixins import PositionMixin
from congo.utils.models import get_model
from congo.utils.text import slugify
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, pgettext
import copy
import importlib
import os
import re

@python_2_unicode_compatible
class AbstractConfig(models.Model):
    """Abstrakcyjny model Configu. Służy do przechowywania zmiennych globalnych"""

    name = models.SlugField(max_length = 255, unique = True, verbose_name = _(u"Nazwa"))
    value = models.CharField(blank = True, max_length = 255, verbose_name = _(u"Wartość"))
    description = models.TextField(null = True, blank = True, verbose_name = _(u"Opis"))
    use_cache = models.BooleanField(default = False, verbose_name = _(u"Cachuj"))
    load_at_startup = models.BooleanField(default = False, verbose_name = _(u"Uruchamiaj przy starcie"))

    class Meta:
        verbose_name = _(u"Parametr systemu")
        verbose_name_plural = _(u"Parametry systemu")
        ordering = ('name',)
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def get_value(cls, name, default = None):
        global CONFIG_CACHE
        name = slugify(name)

        if name in CONFIG_CACHE:
            return CONFIG_CACHE[name]
        try:
            config = cls.objects.get(name = name)
            if config.use_cache:
                CONFIG_CACHE[name] = config.value
            return config.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, name, value):
        name = slugify(name)
        config, created = cls.objects.update_or_create(name = name, defaults = {'value': value})

        if config.use_cache:
            CONFIG_CACHE[name] = value

    @classmethod
    def load_cache(cls):
        global CONFIG_CACHE

        for name, value in cls.objects.filter(use_cache = True, load_at_startup = True).values_list('name', 'value'):
            CONFIG_CACHE[name] = value

    @classmethod
    def clear_cache(cls):
        global CONFIG_CACHE

        CONFIG_CACHE = {}

def clear_config_cache(sender, **kwargs):
    instance = kwargs['instance']

    try:
        del CONFIG_CACHE[instance.name]
    except KeyError:
        pass

# Usage
# from django.db.models.signals import pre_save, pre_delete
# pre_save.connect(clear_config_cache, sender = Config)
# pre_delete.connect(clear_config_cache, sender = Config)

@python_2_unicode_compatible
class AbstractSite(models.Model):
    """Abstrakcyjny model Site. Używany jest gdy na jednej aplikacji uruchomione jest jednocześnie kilka stron"""

    domain = models.CharField(_(u"Domena"), max_length = 100)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, verbose_name = _(u"Język"))
    is_active = models.BooleanField(_(u"Aktywny"), default = False)

    objects = SiteManager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = _(u"Strona")
        verbose_name_plural = _(u"Strony")
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

@python_2_unicode_compatible
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

    name = models.CharField(_(u"Źródło"), max_length = 255, db_index = True)
    level = models.IntegerField(_(u"Poziom"), default = INFO, choices = LEVEL_CHOICE)
    message = models.CharField(_(u"Opis"), max_length = 255)
    user = models.CharField(_(u"Użytkownik"), max_length = 255, null = True, blank = True, db_index = True)
    date = models.DateTimeField(_(u"Data"), auto_now_add = True, db_index = True)
    args = models.TextField(_(u"Szczegóły"), null = True, blank = True)

    class Meta:
        verbose_name = _(u"Log systemowy")
        verbose_name_plural = _(u"Logi systemowe")
        ordering = ('-id',)
        abstract = True

    def __str__(self):
        return u"%s: %s" % (self.get_level_name(self.level), self.name)

    @classmethod
    def is_valid_level(cls, level):
        level_dict = dict(cls.LEVEL_CHOICE)
        return level in level_dict.keys()

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
        return """<span class="%s">%s</span>""" % (css_class, label)

def get_test_choice():
    """Metoda pozwalająca na dynamiczne dodawanie Audytów. Wystarczy wgrać plik z audytem do folderu CONGO_TEST_CHOICE_PATH"""
    test_choice_path = settings.CONGO_TEST_CHOICE_PATH
    if test_choice_path:
        return [(filename, filename) for filename in os.listdir(test_choice_path) if re.match("^(?!_)([a-z_]+).py$", filename, re.IGNORECASE)]
    return []

@python_2_unicode_compatible
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
        (EVERY_MINUTE, _(u"Co minutę")), # eg. every min
        (EVERY_HOUR, _(u"Co godzinę")),
        (EVERY_DAY, _(u"Co dzień")),
        (EVERY_WEEK, _(u"Co tydzień")),
        (EVERY_MONTH, _(u"Every month")),
    )

    test = models.CharField(_(u"Test"), max_length = 255, unique = True, choices = TEST_CHOICE)
    level = models.IntegerField(_(u"Poziom"), default = INFO, choices = LEVEL_CHOICE)
    frequency = models.IntegerField(_(u"Częstotliwość"), choices = FREQUENCY_CHOICE)
    is_active = models.BooleanField(_(u"Aktywny"), default = False)
    last_run_date = models.DateTimeField(_("Ostatnie uruchomienie"), null = True, blank = True)
    result = models.NullBooleanField(_(u"Wynik"), default = None)
    details = models.TextField(_(u"Szczegóły"), null = True, blank = True)
    auditors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank = True, limit_choices_to = {'is_staff': True}, related_name = 'user_audits', verbose_name = _(u"Audytorzy"))

    class Meta:
        verbose_name = _(u"Audyt systemu")
        verbose_name_plural = _(u"Audyty systemu")
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

@python_2_unicode_compatible
class AbstractCron(PositionMixin):
    """Abstrakcyjny model CRON. CRON-y to uruchamiane regularnie zadania, np. czyszczenie logów"""

    JOB_CHOICE = get_job_choice()

    EVERY_MINUTE = 10
    EVERY_HOUR = 20
    EVERY_DAY = 30
    EVERY_WEEK = 40
    EVERY_MONTH = 50
    WORKING_HOURS = 60
    AFTER_HOURS = 70
    MORNINGS_EVENINGS = 80
    EVERY_TEN_MINUTE = 90
    EVERY_THREE_MINUTE = 100
    EVERY_DAY_AT_NOON = 110

    FREQUENCY_CHOICE = (
        (EVERY_MINUTE, _(u"Co minutę")), # eg. every min
        (EVERY_THREE_MINUTE, _(u"Co trzy minuty")), # eg. every 3 min
        (EVERY_TEN_MINUTE, _(u"Co 10 minut")), # eg. every 10 min
        (EVERY_HOUR, _(u"Co godzinę")), # eg. 5 past hour
        (EVERY_DAY, _(u"Co dzień")), # eg. 10 past midnight
        (EVERY_WEEK, _(u"Co tydzień")), # eg. 15 past midnight on mon
        (EVERY_MONTH, _(u"Co miesiąc")), # eg. 20 past midnight on 1-st month day
        (WORKING_HOURS, _(u"W godzinach pracy")), # eg. every 5 min from 8 am to 7 pm mon to sat
        (AFTER_HOURS, _(u"Po godzinach")), # eg. every 3 min from 5 pm to 9 pm mon to sat
        (MORNINGS_EVENINGS, _(u"Rano i wieczorem")), # eg. 7:55 am and 7:55 pm
        (EVERY_DAY_AT_NOON, _(u"Co dzień w południe")), # eg. 12 pm
    )

    job = models.CharField(_(u"Zadanie"), max_length = 255, unique = True, choices = JOB_CHOICE)
    frequency = models.IntegerField(_(u"Częstotliwość"), choices = FREQUENCY_CHOICE)
    is_active = models.BooleanField(_(u"Aktywny"), default = False)
    last_run_date = models.DateTimeField(_("Ostatnie uruchomienie"), null = True, blank = True)

    class Meta:
        verbose_name = _(u"Zadanie CRON")
        verbose_name_plural = _(u"Zadania CRON")
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

@python_2_unicode_compatible
class AbstractUrlRedirect(models.Model):
    """Abstrakcyjny model przekierowań URL"""

    old_url = models.CharField(_(u"Stary URL"), max_length = 255, db_index = True, help_text = _(u"Format: ^/old-url/$"))
    redirect_url = models.CharField(_(u"Nowy URL"), max_length = 255, help_text = _(u"Format: /new-url/"))
    rewrite_tail = models.BooleanField(_(u"Przepisać ogon"), default = False, help_text = _(u"Czy zamienić /old-url/abc/ na /new-url/abc/ czy jedynie /new-url/?"))
    is_permanent_redirect = models.BooleanField(_(u"Permanentne przekierowanie?"), default = True, help_text = _(u"Czy przekierowanie jest permanentne (301) czy tymczasowe (302)?"))

    class Meta:
        verbose_name = _(u"Przekierowanie URL")
        verbose_name_plural = _(u"Przekierowania URL")
        ordering = ('old_url',)
        abstract = True

    def __str__(self):
        return u"%s > %s" % (self.old_url, self.redirect_url)

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
                print ""
                print "%s > %s" % (redirect.old_url, redirect.redirect_url)
                print "  rewrite_tail: %s, is_permanent_redirect %s" % (redirect.rewrite_tail, redirect.is_permanent_redirect)
                print ""

            if redirect.rewrite_tail:
                redirect_url = old_url.replace(redirect.old_url.replace('^', '').replace('$', ''), redirect.redirect_url)
            else:
                redirect_url = redirect.redirect_url

            return (redirect_url, redirect.is_permanent_redirect)
        except IndexError:

            return (None, None)

@python_2_unicode_compatible
class AbstractHoliday(models.Model):
    """Abstrakcyjny model wolnego. Pokazuje dni wolne od pracy i dni pracujące"""

    date = models.DateField(db_index = True, verbose_name = _(u"Data"))
    description = models.CharField(max_length = 255, blank = True, verbose_name = _(u"Opis"))
    is_working_day = models.BooleanField(default = False, verbose_name = _(u"Czy dzień pracujący"))

    class Meta:
        verbose_name = _(u"Dzień świąteczny")
        verbose_name_plural = u"Dni świąteczne"
        ordering = ('-date',)
        abstract = True

    def __str__(self):
        if self.description:
            return u"%s (%s)" % (self.description, self.date)
        else:
            return u"%s" % self.date

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
        periods = [pgettext('weekday', u"Pn. - Pt."), pgettext('weekday', u"Sb."), pgettext('weekday', u"Nd.")]
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

