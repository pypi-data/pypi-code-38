# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import models
from django_szuprefix.utils import statutils


def stats_course(qset=None, measures=None, period=None):
    if qset is None:
        qset = models.Course.objects.all()

    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'create_time')
    funcs = {
        'today': lambda: dstat.stat("今天", only_first=True),
        'yesterday': lambda: dstat.stat("昨天", only_first=True),
        'all': lambda: qset.count(),
        'daily': lambda: dstat.stat(period),
    }
    return dict([(m, funcs[m]()) for m in measures])
