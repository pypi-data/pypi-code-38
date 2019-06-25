# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import models
from django_szuprefix.utils import dateutils, statutils
from django.db.models import Count


def stats_student(qset=None, measures=None, period=None):
    qset = qset if qset is not None else models.Student.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'create_time')
    qset_unbind = qset.filter(is_bind=False)
    funcs = {
        'today': lambda: dstat.stat("今天", only_first=True),
        'yesterday': lambda: dstat.stat("昨天", only_first=True),
        'all': lambda: qset.count(),
        'daily': lambda: dstat.stat(period),
        'bind': lambda: get_student_bind_events(qset.values_list('id', flat=True)).count(),
        'bind_daily': lambda: statutils.DateStat(get_student_bind_events(list(qset.values_list('id', flat=True))),'create_time').stat(period),
        'unbind': lambda: qset_unbind.count(),
        'unbind_clazzs': lambda: statutils.count_by(qset_unbind, 'clazz__name', distinct=True, sort="-")
    }
    return dict([(m, funcs[m]()) for m in measures])


def get_student_bind_events(sids):
    from django_szuprefix.common.models import Event
    qset = Event.objects.filter(content_type__app_label='school', content_type__model='Student', name='bind')
    qset = statutils.using_stats_db(qset)
    qset = qset.filter(object_id__in=sids)
    return qset


def stats_teacher(qset=None, measures=None, period=None):
    qset = qset if qset is not None else models.Teacher.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'create_time')
    funcs = {
        'today': lambda: dstat.stat("今天", only_first=True),
        'yesterday': lambda: dstat.stat("昨天", only_first=True),
        'all': lambda: qset.count(),
        'daily': lambda: dstat.stat(period)
    }
    return dict([(m, funcs[m]()) for m in measures])


def stats_clazz(qset=None, measures=None, period=None):
    qset = qset if qset is not None else models.Clazz.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'create_time')
    funcs = {
        'today': lambda: dstat.stat("今天", only_first=True),
        'yesterday': lambda: dstat.stat("昨天", only_first=True),
        'all': lambda: qset.count(),
        'daily': lambda: dstat.stat(period)
    }
    return dict([(m, funcs[m]()) for m in measures])
