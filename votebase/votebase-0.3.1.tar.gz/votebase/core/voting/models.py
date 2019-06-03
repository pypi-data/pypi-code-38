import hashlib
import random
from django.conf import settings

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EMPTY_VALUES
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from votebase.core.surveys.models import Survey, Round
from votebase.core.utils.helpers import get_class
from votebase.core.voting.managers import AnswerManager, VoterQuerySet, VotedQuestionManager
from votebase.core.questions.models import Question, Option


class Voter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'user'),
        default=None, null=True, blank=True)
    survey = models.ForeignKey(Survey, verbose_name=_(u'survey'))
    round = models.ForeignKey(Round, verbose_name=_(u'segment'))
    quiz_result = models.FloatField(verbose_name=_(u'quiz result'), db_index=True,
        default=None, null=True, blank=True)
    hash_key = models.CharField(_(u'hash key'), max_length=255, db_index=True,
        default=None, blank=True, null=True)
    ip_address = models.CharField(_(u'IP address'), max_length=255)
    latitude = models.CharField(
        _(u'latitude'), max_length=255, null=True, blank=True, default=None)
    longitude = models.CharField(
        _(u'longitude'), max_length=255, null=True, blank=True, default=None)
    continent_code = models.CharField(
        _(u'continent code'), max_length=255, null=True, blank=True,
        default=None)
    country_name = models.CharField(
        _(u'country name'), max_length=255, null=True, blank=True,
        default=None)
    country_code = models.CharField(
        _(u'country code'), max_length=255, null=True, blank=True,
        default=None)
    city = models.CharField(
        _(u'city'), max_length=255, null=True, blank=True, default=None)
    area_code = models.CharField(
        _(u'area code'), max_length=255, null=True, blank=True, default=None)
    voting_started = models.DateTimeField(_(u'voting started'),
        null=True, blank=True, default=None)
    voting_ended = models.DateTimeField(_(u'voting ended'),
        null=True, blank=True, default=None)
    voting_duration = models.PositiveIntegerField(_(u'voting duration'), db_index=True,
        null=True, blank=True, default=None)
    flag = models.CharField(_(u'custom flag'), max_length=256,
        null=True, blank=True, default=None)
    is_quiz_result_sent = models.BooleanField(_(u'quiz result sent'), default=False, db_index=True)
    is_api_voter = models.BooleanField(_(u'API voter'), default=False)
    is_irrelevant = models.BooleanField(_(u'irrelevant'), default=False)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))
    objects = VoterQuerySet.as_manager()

    class Meta:
        app_label = 'voting'
        db_table = 'votebase_voters'
        verbose_name = _(u'voter')
        verbose_name_plural = _(u'voters')
        ordering = ('-created', )

    def __unicode__(self):
        try:
            if self.user:
                return self.user.get_profile().get_full_name()
        except ObjectDoesNotExist:
            pass
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        """ URL for survey owner """
        return 'statistics_voter', (str(self.pk), )

    @models.permalink
    def get_absolute_hash_url(self):
        """ URL for voter """
        return 'statistics_voter_hash', (str(self.hash_key), )

    @models.permalink
    def get_absolute_history_url(self):
        """ URL for voter who is registered """
        return 'statistics_voter_history', (str(self.hash_key), )

    @property
    def voted_questions(self):
        return VotedQuestion.objects.get_voter_questions(self)

    @property
    # @cached_property
    def categories(self):
        return list(set(self.voted_questions.order_by('weight').values_list('category', flat=True)))

    def has_categories(self):
        return len(self.categories) > 0 and self.categories[0] not in EMPTY_VALUES

    def get_voting_duration_timedelta(self):
        return self.voting_ended - self.voting_started

    def get_question_result(self, question):
        # Get result from cache
        result = cache.get('voter_question_{}_result'.format(question.pk), version=self.pk)

        if result is None:
            try:
                result = question.get_voter_form_class().get_result(question, self)
            except AttributeError:
                result = None

        cache.set('voter_question_{}_result'.format(question.pk), result, version=self.pk, timeout=60*60*12)
        return result

    def get_quiz_result(self, questions=None):
        quiz_result_handler_name = getattr(settings, 'VOTEBASE_QUIZ_RESULT_HANDLER', 'votebase.core.voting.handlers.quiz_result')
        quiz_result_handler = get_class(quiz_result_handler_name)
        return quiz_result_handler(self, questions)

    def send_quiz_result(self):
        quiz_result_mail_handler_name = getattr(settings, 'VOTEBASE_QUIZ_RESULT_MAIL_HANDLER', 'votebase.core.utils.mail.send_quiz_result_to_voter_in_background')
        quiz_result_mail_handler = get_class(quiz_result_mail_handler_name)
        return quiz_result_mail_handler.delay(self)

    def generate_unique_hash(self):
        while True:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            hash_key = hashlib.sha1(salt + str(self.pk)).hexdigest()

            if not Voter.objects.filter(hash_key=hash_key).count():
                break

        return hash_key

    def save(self, **kwargs):
        self.modified = now()

        if self.hash_key in EMPTY_VALUES:
            self.hash_key = self.generate_unique_hash()

        # quiz_result = self.get_quiz_result()
        # print(quiz_result)

        super(Voter, self).save(**kwargs)


class VotedQuestion(models.Model):
    voter = models.ForeignKey(Voter, verbose_name=_(u'voter'))
    question = models.ForeignKey(Question, verbose_name=_(u'question'))
    weight = models.PositiveIntegerField(_(u'weight'), default=0, db_index=True)
    page = models.PositiveIntegerField(_(u'page'), default=1)
    quiz_result = models.FloatField(verbose_name=_(u'quiz result'), db_index=True,
        default=None, null=True, blank=True)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))
    objects = VotedQuestionManager()

    class Meta:
        app_label = 'voting'
        db_table = 'votebase_voted_questions'
        verbose_name = _(u'voted question')
        verbose_name_plural = _(u'voted questions')
        ordering = ('weight', 'pk')

    def __unicode__(self):
        return self.question.title

    def save(self, **kwargs):
        self.modified = now()

        # save quiz result
        if self.quiz_result is None and self.question.survey.is_quiz():
            self.quiz_result = self.voter.get_question_result(self.question)

        super(VotedQuestion, self).save(**kwargs)

    @property
    def answer_set(self):
        return Answer.objects.filter(question=self.question, voter=self.voter)


class Answer(models.Model):
    ORIENTATION_ROW = 'ROW'
    ORIENTATION_COLUMN = 'COLUMN'
    ORIENTATIONS = (
        (ORIENTATION_ROW, _(u'Row')),
        (ORIENTATION_ROW, _(u'Column')),
    )

    voter = models.ForeignKey(Voter, verbose_name=_(u'voter'))
    question = models.ForeignKey(Question, verbose_name=_(u'question'))
    custom = models.TextField(
        _(u'custom'), null=True, blank=True, default=None)
    option = models.ForeignKey(
        Option, verbose_name=_(u'option'), default=None, null=True, blank=True)
    option_column = models.ForeignKey(
        Option, verbose_name=_(u'option column'), default=None, null=True,
        blank=True, related_name='option_column')
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))
    objects = AnswerManager()

    class Meta:
        app_label = 'voting'
        db_table = 'votebase_answers'
        verbose_name = _(u'answer')
        verbose_name_plural = _(u'answers')
        ordering = ('-created', )

    def __unicode__(self):
        return str(self.pk)

    def save(self, **kwargs):
        self.modified = now()
        super(Answer, self).save(**kwargs)
