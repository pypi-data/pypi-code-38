# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from parler.managers import TranslatableManager


class TranslatableVisibleManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są widoczne.
    """

    def get_queryset(self):
        return super(TranslatableVisibleManager, self).get_queryset().filter(is_visible = True)


class TranslatableActiveManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są aktywne.
    """

    def get_queryset(self):
        return super(TranslatableActiveManager, self).get_queryset().filter(is_active = True)


class TranslatableOnSiteManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(TranslatableOnSiteManager, self).get_queryset().filter(sites__id = settings.SITE_ID)


class TranslatableVisibleOnSiteManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są widoczne (is_visible) oraz przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(TranslatableVisibleOnSiteManager, self).get_queryset().filter(translations__language_code = settings.PARLER_LANGUAGES[settings.SITE_ID][0]['code'], is_visible = True, sites__id = settings.SITE_ID)


class TranslatableVisibleCurrentOnSiteManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są widoczne, aktywne (data) oraz przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(TranslatableVisibleCurrentOnSiteManager, self).get_queryset().filter(is_visible = True, start_date__lte = timezone.now(), end_date__gte = timezone.now(), sites__id = settings.SITE_ID)


class TranslatableVisibleCurrentManager(TranslatableManager):
    """
    Manager dla tłumaczonych modeli. Zwraca obiekty które są widoczne oraz przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(TranslatableVisibleCurrentManager, self).get_queryset().filter(is_visible = True, start_date__lte = timezone.now(), end_date__gte = timezone.now())
