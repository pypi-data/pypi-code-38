# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models

import logging

log = logging.getLogger('django')


@receiver(post_save, sender=models.Answer)
def cal_performance(sender, **kwargs):
    try:
        created = kwargs['created']
        if not created:
            return
        answer = kwargs['instance']
        paper = answer.paper
        performance, created = paper.performances.update_or_create(paper=paper, party=answer.party, user=answer.user)

        stat, created = models.Stat.objects.get_or_create(paper=paper, party=answer.party)
        stat.add_answer(answer)
        # print 'stat'
        stat.save()
    except Exception, e:
        import traceback
        log.error("exam cal_performance with answer %s error:%s", answer.id, traceback.format_exc())
