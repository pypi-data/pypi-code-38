# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """
    Manager zwracający obiekty, których atrybut is_active = True.
    """

    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active = True)

class VisibleManager(models.Manager):
    """
    Manager zwraca obiekty które sa widoczne (is_visible = True).
    """

    def get_queryset(self):
        return super(VisibleManager, self).get_queryset().filter(is_visible = True)

class CurrentManager(models.Manager):
    """
    Zwraca aktywne obiekty. Obiekt jest aktywny wtedy, gdy dzisiejsza data znajduje się pomiedzy start_date a end_date.
    
    W przypadku gdy start_date_field_name i end_date_field_name nie nazywają się 'start_date' i 'end_date': 
    current_manager = Model.CurrentManager(start_date_field_name = 'nazwa_start_date', end_date_field_name = 'nazwa_end_date')
    
    lub w przypadku gdy start_date_field_name i end_date_field_name nazywają się 'start_date' i 'end_date':
    current_manager = Model.CurrentManager()
    """

    def __init__(self, start_date_field_name = 'start_date', end_date_field_name = 'end_date'):
        super(CurrentManager, self).__init__()
        self._start_date_field_name = start_date_field_name
        self._end_date_field_name = end_date_field_name

    def _get_kwargs(self):
        start_date_lookup = '%s_lte' % self._start_date_field_name
        end_date_lookup = '%s_gte' % self._end_date_field_name
        now = timezone.now()
        return {
            start_date_lookup: now,
            end_date_lookup: now
        }

    def get_queryset(self):
        return super(CurrentManager, self).get_queryset().filter(**self._get_kwargs())

class OnSiteManager(models.Manager):
    """
    Manager zwracający obiekty, których site_id = settings.SITE_ID (zwraca obiekty, które są przypisane do aktywnego site'a.
    
    Jeśli FK/M2M do site'a nie nazywa się 'site' lub 'sites':
    on_site_manager = Model.OnSiteManager('site_field_name')
    
    
    Jeśli FK/M2M do site'a nazywa się 'site' lub 'sites':
    on_site_manager = Model.OnSiteManager()
    """

    def __init__(self, site_field_name = None):
        super(OnSiteManager, self).__init__()
        self._site_field_name = site_field_name
        self._site_field = None

    def _get_site_field_name(self):
        if not self._site_field_name:
            try:
                site_field_name = 'site'
                self.model._meta.get_field(site_field_name)
            except FieldDoesNotExist:
                site_field_name = 'sites'
            self._site_field_name = site_field_name
        return self._site_field_name

    def _get_site_field(self):
        if not self._site_field:
            self._site_field = self.model._meta.get_field(self._get_site_field_name())
        return self._site_field

    def _get_kwargs(self):
        site_field_name = self._get_site_field_name()

        if isinstance(site_field_name, models.ManyToManyField):
            lookup = '%s__id__in' % site_field_name
        else:
            lookup = '%s__id' % site_field_name
        return {
            lookup: settings.SITE_ID
        }

    def get_queryset(self):
        return super(OnSiteManager, self).get_queryset().filter(**self._get_kwargs())

class ActiveOnSiteManager(OnSiteManager):
    """
    Manager zwraca obiekty, które są jednocześnie aktywne i są przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active = True)

class ActiveCurrentManager(CurrentManager):
    """
    Manager zwraca obiekty, które są jednocześnie obiekty aktywne (data) oraz aktywne (is_active).
    """

    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active = True)

class CurrentOnSiteManager(CurrentManager, OnSiteManager):
    """
    Manager zwraca obiekty, które są jednocześnie aktywne (data) oraz są przypisane do aktywnej strony.
    """

    def __init__(self, start_date_field_name = 'start_date', end_date_field_name = 'end_date', site_field_name = None):
        CurrentManager.__init__(self, start_date_field_name, end_date_field_name)
        self._site_field_name = site_field_name

    def get_queryset(self):
        kwargs = OnSiteManager._get_kwargs(self)
        return CurrentManager.get_queryset(self).filter(**kwargs)

class VisibleOnSiteManager(models.Manager):
    """
    Manager zwraca obiekty które są widoczne oraz przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(VisibleOnSiteManager, self).get_queryset().filter(is_visible = True, sites__id = settings.SITE_ID)

class VisibleCurrentOnSiteManager(models.Manager):
    """
    Manager zwraca obiekty które są jednocześnie widoczne (is_visible), aktywne (data) oraz przypisane do aktywnej strony.
    """

    def get_queryset(self):
        return super(VisibleCurrentOnSiteManager, self).get_queryset().filter(is_visible = True, start_date__lte = timezone.now(), end_date__gte = timezone.now(), sites__id = settings.SITE_ID)
