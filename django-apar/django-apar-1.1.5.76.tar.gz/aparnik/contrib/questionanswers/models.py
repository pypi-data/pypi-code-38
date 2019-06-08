# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from aparnik.contrib.reviews.models import BaseReview, BaseReviewManager
from aparnik.contrib.filefields.models import FileField

User = get_user_model()


# QA MANAGER
class QAManager(BaseReviewManager):

    def get_queryset(self):
        return super(QAManager, self).get_queryset()

    def get_this_user(self, user):
        return super(QAManager, self).get_this_user(user=user)

    def model_question_answer(self, model_obj, user_obj=None, with_children=False):
        return super(QAManager, self).model_base_reviews(model_obj, user_obj, with_children=with_children)

    def model_question_answer_count(self, model_obj, user_obj=None):
        return self.model_question_answer(model_obj, user_obj, with_children=True).count()


# QA MODEL
class QA(BaseReview):
    files = models.ManyToManyField(FileField, blank=True, verbose_name=_('Files'))

    objects = QAManager()

    class Meta:
        verbose_name = _('Question Answer')
        verbose_name_plural = _('Questions Answers')

    def __unicode__(self):
        return self.title
