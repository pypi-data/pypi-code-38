# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import datetime

from django.contrib.admin import DateFieldListFilter, SimpleListFilter
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _


class MyDateListFilter(DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(MyDateListFilter, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        
        # копия оригинального кода из DateFieldListFilter,
        # т.к. локальные переменные и заюзать их нельзя 
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:       # field is a models.DateField
            today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        # копия end
        yesterday = today - datetime.timedelta(days=1)
        
        # втыкаем наши пункты
        self.links = list(self.links)
        self.links.insert(
            1,
            (_('The day after tomorrow'), {
                self.lookup_kwarg_since: str(tomorrow + datetime.timedelta(days=1)),  # >=
                self.lookup_kwarg_until: str(tomorrow + datetime.timedelta(days=2)),  # <
            })
        )
        self.links.insert(
            2,
            (_('Tomorrow'), {
                self.lookup_kwarg_since: str(tomorrow),  # >=
                self.lookup_kwarg_until: str(tomorrow + datetime.timedelta(days=1)),  # <
            })
        )
        self.links.insert(
            4,
            (_('Yesterday'), {
                self.lookup_kwarg_since: str(yesterday),  # >=
                self.lookup_kwarg_until: str(today),  # <
            })
        )
        self.links.insert(
            5,
            (_('The day before yesterday'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=2)),  # >=
                self.lookup_kwarg_until: str(yesterday),  # <
            })
        )


class MyDateListFilterNoFuture(MyDateListFilter):  # no future, посоны
    """Тот же фильтр, но без дат в будущем."""
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(MyDateListFilterNoFuture, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        del self.links[2]
        del self.links[1]


class MyNullNotNullFilter(SimpleListFilter):
    """
    Если поле хранит что-то и может быть NULL (в терминах БД), а в админке этот
    фильтр сводит всё до заполнено поле (любое значение, в том числе 0, ''...)
    или не заполнено (только IS NULL).
    
    Пример:
    # filters.py
    MyIsDoneFilter(MyNullNotNullFilter):
        title = 'Сделано ли задание'
        parameter_name = 'done_at'  # поле хранит дату, когда сделано или NULL
    
    # admin.py
    list_filter = [ MyIsDoneFilter, ]
    """

    title = None
    parameter_name = None

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes'),),
            ('0', _('No'),),
        )

    def queryset(self, request, queryset):
        kwargs = { '%s' % self.parameter_name : None, }
        if self.value() == '0':
            return queryset.filter(**kwargs)
        if self.value() == '1':
            return queryset.exclude(**kwargs)
        return queryset


class AuthorListFilter(SimpleListFilter):
    title = _('author')
    parameter_name = 'author_id_filter'
    
    def lookups(self, request, model_admin):
        ret = []
        authors = User.objects.filter(is_staff=True, is_active=True) \
                    .order_by('first_name', 'last_name', 'username')
        for author in authors:
            ret.append((
                str(author.id),
                author.get_full_name() if author.get_full_name() \
                else author.get_username(),
            ))
        return ret
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(author_id=self.value())

