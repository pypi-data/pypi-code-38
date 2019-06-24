# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.functional import cached_property

from django_szuprefix_saas.saas.models import Party
from django.contrib.auth.models import User
from django_szuprefix.utils import modelutils

EXAM_MIN_PASS_SCORE = 70


class Paper(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "试卷"
        ordering = ('-is_active', 'title', '-create_time',)
        permissions = (
            ("view_all_paper", "查看所有试卷"),
        )

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_papers",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_papers",
                             on_delete=models.PROTECT)
    title = models.CharField("标题", max_length=255, blank=False)
    content = models.TextField("内容", blank=True, null=True,
                               help_text="编辑指南:\n首行为标题.\n题型用中文数字加点号开头.\n题目用阿拉伯数字加点号开头.\n答案选项用英文字母加点号开头.\n正确答案用'答案:'开头")
    content_object = modelutils.JSONField("内容对象", blank=True, null=True, help_text="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", blank=False)
    questions_count = models.PositiveSmallIntegerField("题数", blank=True, default=0)
    is_break_through = models.BooleanField("闯关", blank=True, default=True)

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.title:
            self.title = "试卷"
        if self.is_break_through is None:
            self.is_break_through = True
        data = self.content_object
        if data:
            self.questions_count = data.get("questionCount", 0)
        return super(Paper, self).save(**kwargs)


class Stat(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "统计"

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_stats",
                              on_delete=models.PROTECT)
    paper = models.OneToOneField(Paper, verbose_name=Paper._meta.verbose_name, related_name="stat",
                                 on_delete=models.PROTECT)
    detail = modelutils.JSONField("详情", help_text="")

    def __unicode__(self):
        return "统计<%s>" % self.paper

    def add_answer(self, answer):
        d = self.detail or {}
        from . import helper
        questions = d.setdefault('questions', {})
        score_level = str(answer.performance.get('stdScore', 0) / 5 * 5)
        helper.distrib_count(d.setdefault('scores', {}), score_level)
        seconds_level = str((answer.seconds / 60 + 1) * 60)
        helper.distrib_count(d.setdefault('seconds', {}), seconds_level)
        ad = answer.detail
        for a in ad:
            num = str(a.get('number'))
            questions[num] = questions.setdefault(num, 0) + (a.get('right') is False and 1 or 0)
        d['answer_user_count'] = self.paper.answers.values('user').distinct().count()
        self.detail = d


class Answer(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "用户答卷"
        ordering = ('-create_time',)
        permissions = (
            ("view_all_answer", "查看所有用户答卷"),
        )


    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_answers",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_answers",
                             on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, verbose_name=Paper._meta.verbose_name, related_name="answers",
                              on_delete=models.PROTECT)
    detail = modelutils.JSONField("详情", help_text="")
    seconds = models.PositiveSmallIntegerField("用时", default=0, blank=True, null=True, help_text="单位(秒)")
    std_score = models.PositiveSmallIntegerField("分数", default=0, blank=True, null=True)
    performance = modelutils.JSONField("成绩表现", blank=True, null=True, help_text="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s by %s" % (self.paper, self.user.get_full_name())

    def save(self, **kwargs):
        self.performance = self.cal_performance()
        self.std_score = self.performance.get('stdScore')
        return super(Answer, self).save(**kwargs)

    def cal_performance(self):
        wc = 0
        rc = 0
        score = 0
        fsc = 0

        from .helper import answer_equal, answer_match
        for a in self.detail:
            # sc = a.get('score', 1)
            # fsc += sc
            # m = answer_match(a.get('answer'), a.get('userAnswer'))
            # if m == 1:
            #     a['right'] = True
            #     a['userScore'] = sc
            #     score += sc
            #     rc += 1
            # else:
            #     wc += 1
            #     a['right'] =False
            if a['right'] is True:
                rc += 1
                score += a['userScore']
            else:
                wc += 1
            fsc += a['score']
        return dict(
            wrongCount=wc,
            rightCount=rc,
            fullScore=fsc,
            score=score,
            stdScore=score * 100 / fsc if fsc > 0 else 0
        )


class Performance(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "用户成绩"
        unique_together = ('party', 'user', 'paper')
        # ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_performances",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_performances",
                             on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, verbose_name=Paper._meta.verbose_name, related_name="performances",
                              on_delete=models.PROTECT)
    score = models.PositiveSmallIntegerField("得分", default=0, blank=True, null=True)
    detail = modelutils.JSONField("详情", blank=True, null=True, help_text="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def __unicode__(self):
        return "%s by %s" % (self.paper, self.user)

    @cached_property
    def is_passed(self):
        return self.detail.get('maxScore') >= EXAM_MIN_PASS_SCORE if self.paper.is_break_through else True

    def cal_performance(self):
        answers = self.paper.answers.filter(user=self.user)
        scs = [a.performance.get('stdScore', 0) for a in answers]
        lastAnswer = answers.first()
        times = len(scs)
        return dict(
            maxScore=max(scs),
            minScore=min(scs),
            avgScore=sum(scs) / times,
            lastScore=scs[0],
            times=times,
            scores=scs,
            lastTime=lastAnswer and lastAnswer.create_time.isoformat()
        )

    def save(self, **kwargs):
        p = self.cal_performance()
        self.detail = p
        self.score = p.get('lastScore', 0)
        return super(Performance, self).save(**kwargs)
