from __future__ import unicode_literals

from cms.models import CMSPlugin
from django import forms
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .fields import ColorField


@python_2_unicode_compatible
class Question(models.Model):
    SESSION = 'S'
    USER = 'U'
    question = models.CharField(_('question'), max_length=150)
    limit = models.CharField(
        _('limit'), max_length=1,
        choices=((SESSION, _('1 vote per session')), (USER, _('1 vote per user'))),
        default=SESSION,
    )
    users_voted = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_('users voted'),
        related_name='cmsplugin_survey_votes', editable=False,
    )
    closed = models.BooleanField(_('voting closed'), default=False)

    class Meta:
        app_label = 'cmsplugin_survey'
        ordering = ('-id',)
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __str__(self):
        return self.question

    @property
    def votes(self):
        return Vote.objects.filter(answer__question=self)

    @cached_property
    def votes_count(self):
        return self.votes.count()

    def get_votes(self, t):
        return self.votes.filter(created__lte=t)

    def can_vote(self, request):
        if self.closed:
            return False
        if self.limit == self.SESSION:
            return self.id not in request.session.get('cmsplugin_survey_voted', [])
        else:
            return (request.user.is_authenticated()
                    and not self.users_voted.filter(pk=request.user.pk).exists())

    def set_voted(self, request):
        if self.limit == self.SESSION:
            request.session.setdefault('cmsplugin_survey_voted', [])
            request.session['cmsplugin_survey_voted'].append(self.id)
        else:
            self.users_voted.add(request.user)

    @cached_property
    def answer_form_class(self):
        class AnswerForm(forms.Form):
            answer = forms.ModelChoiceField(
                empty_label=None,
                queryset=self.answers.all(),
                widget=forms.widgets.RadioSelect(attrs={'class': 'survey-input'}),
            )
        return AnswerForm


@python_2_unicode_compatible
class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name=_('question'), related_name='answers')
    answer = models.CharField(_('answer'), max_length=150)
    color = ColorField(_('color'))
    order = models.IntegerField(_('order'), blank=True, default=0)

    class Meta:
        app_label = 'cmsplugin_survey'
        ordering = ('order',)
        verbose_name = _('answer')
        verbose_name_plural = _('answers')

    def __str__(self):
        return self.answer

    @cached_property
    def votes_count(self):
        return self.votes.count()

    @cached_property
    def percents(self):
        return int(round(
            self.votes_count * 100.0 / self.question.votes_count
        )) if self.question.votes_count else 0


class Vote(models.Model):
    answer = models.ForeignKey(Answer, verbose_name=_('answer'), related_name='votes')
    created = models.DateTimeField(_('time'), auto_now_add=True)

    class Meta:
        app_label = 'cmsplugin_survey'
        ordering = ('created',)
        verbose_name = _('vote')
        verbose_name_plural = _('votes')


@python_2_unicode_compatible
class QuestionPlugin(CMSPlugin):
    question = models.ForeignKey(Question, verbose_name=_('question'))
    template = models.CharField(
        _('template'), max_length=100,
        choices=settings.CMSPLUGIN_SURVEY_TEMPLATES,
        default=settings.CMSPLUGIN_SURVEY_TEMPLATES[0][0],
        help_text=_('The template used to render plugin.'),
    )

    class Meta:
        app_label = 'cmsplugin_survey'

    def __str__(self):
        return self.question.question
