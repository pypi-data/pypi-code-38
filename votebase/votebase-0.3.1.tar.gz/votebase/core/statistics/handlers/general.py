from __future__ import division

import unicodecsv

from django.core.validators import EMPTY_VALUES
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from votebase.core.voting.models import Answer


class CsvHandler(object):

    def __init__(self, question, round=None):
        self.question = question
        self.survey = self.question.survey
        self.round = round
        self.response = HttpResponse(mimetype='text/csv')
        self.response['Content-Disposition'] =\
        'attachment;filename="%(filename)s"' % {
            'filename': self.get_filename()
        }

        self.writer = unicodecsv.writer(self.response, encoding='utf-8')
        self.tz = timezone.get_default_timezone()

    def get_filename(self):
        return 's%(survey_id)s_q%(question_id)s_%(qslug)s.csv' % {
            'survey_id': self.question.survey.id,
            'question_id': self.question.id,
            'qslug': slugify(self.question.title),
        }

    def write_header(self):
        self.writer.writerow([_(u'Question statistics'),])
        self.writer.writerow([_(u'Date of export'), now().astimezone(self.tz),])
        self.writer.writerow([])
        self.writer.writerow([_(u'Objects'),])
        self.writer.writerow([
            _(u'Object'),
            _(u'ID'),
            _(u'Title'),
            _(u'Created'),
            ])

        # QUESTION
        question_created = self.question.created.astimezone(self.tz)
        self.writer.writerow([
            _(u'Question'),
            self.question.id, self.question.title, question_created])

        # ROUND
        if self.round is not None:
            segment_created = self.round.created.astimezone(self.tz)
            self.writer.writerow([
                _(u'Segment'),
                self.round.id, self.round.title, segment_created])

        # SURVEY
        survey_created = self.survey.created.astimezone(self.tz)
        self.writer.writerow([
            _(u'Survey'),
            self.survey.id, self.survey.title, survey_created])

        self.writer.writerow([])

    def count_answers(self):
        if self.round is not None:
            self.answers = Answer.objects.filter(
                question=self.question, voter__round=self.round, voter__is_irrelevant=False).distinct()
#            self.voters = self.round.voter_set.all().filter(pk__in=self.answers.values('voter_id'))

        else:
            self.answers = Answer.objects.filter(
                question=self.question, voter__is_irrelevant=False).distinct()
#            self.voters = self.survey.voter_set.all().filter(pk__in=self.answers.values('voter_id'))

        # total count
        self.total_answers_count = self.answers.count()
#        self.total_voters_count = self.voters.count()
        self.total_voters_count = self.answers.values('voter').distinct().count()

    def export(self):
        return self.response


class OptionsQuestionCsvHandler(CsvHandler):
    def write_options(self):
        # set option information
        self.options = []
        for option in self.question.option_set.all():
            option_answers = self.answers.filter(option=option)
            count = option_answers.count()

            try:
                percent = count * 100 / self.total_answers_count
            except ZeroDivisionError:
                percent = 0

            self.options.append({
                'id': option.id,
                'title': option.title,
                'count': count,
                'percent': round(percent, 2)
            })

        #HEADER
        self.writer.writerow([_(u'Options'),])
        self.writer.writerow([
            _(u'ID'),
            _(u'Title'),
            _(u'Count'),
            _(u'Percent'),
            ])

        for option in self.options:
            self.writer.writerow([
                option['id'],
                option['title'],
                option['count'],
                '%s%%' % option['percent']
            ])

        self.writer.writerow([
            '',
            _(u'Total answers'),
            self.total_answers_count
        ])

        self.writer.writerow([])

    def write_answers(self):
        self.writer.writerow([_(u'Answers and voters'),])
        self.writer.writerow([_(u'Total answers'), self.total_answers_count,])
        self.writer.writerow([_(u'Total voters'), self.total_voters_count,])
        self.writer.writerow([
            _(u'Answer ID'),
            _(u'Voter ID'),
            _(u'User ID'),
            _(u'User fullname'),
            #            _(u'Question ID'),
            #            _(u'Question Title'),
            _(u'Option ID'),
            _(u'Option title'),
            _(u'Created'),
            ])

        for answer in self.answers:
            # user
            user = answer.voter.user
            user_id = '' if user is None else user.id
            full_name = '' if user is None else user.get_profile().get_full_name()

            # option
            option = answer.option
            option_id = '' if option is None else option.id
            option_title = '' if option is None else option.title

            self.writer.writerow([
                answer.id,
                answer.voter.id,
                user_id,
                full_name,
                #                answer.question.id,
                #                answer.question.title,
                option_id,
                option_title,
                answer.created.astimezone(self.tz)
            ])

    def export(self):
        self.count_answers()
        self.write_header()
        self.write_options()
#        self.write_answers()
        return super(OptionsQuestionCsvHandler, self).export()


class TextQuestionCsvHandler(CsvHandler):
    def write_customs(self):
        # order by count
        answers = self.answers.values('custom').annotate(count=Count('pk')).order_by('-count')

        # set option information
        self.customs = []
        for answer in answers:
            count = answer['count']

            try:
                percent = count * 100 / self.total_answers_count
            except ZeroDivisionError:
                percent = 0

            custom_title = _(u'Empty') if answer['custom'] in EMPTY_VALUES else answer['custom']

            self.customs.append({
                'title': custom_title,
                'count': count,
                'percent': round(percent, 2)
            })

        #HEADER
        self.writer.writerow([_(u'Entered values'),])
        self.writer.writerow([
            _(u'Text'),
            _(u'Count'),
            _(u'Percent'),
            ])

        for option in self.customs:
            self.writer.writerow([
                option['title'],
                option['count'],
                '%s%%' % option['percent']
            ])

        self.writer.writerow([
            '',
            _(u'Total answers'),
            self.total_answers_count
        ])

        self.writer.writerow([])

    def write_answers(self):
        self.writer.writerow([_(u'Answers and voters'),])
        self.writer.writerow([_(u'Total different values'), self.total_answers_count,])
        self.writer.writerow([_(u'Total voters'), self.total_voters_count,])
        self.writer.writerow([
            _(u'Answer ID'),
            _(u'Voter ID'),
            _(u'User ID'),
            _(u'User fullname'),
            #            _(u'Question ID'),
            #            _(u'Question Title'),
            _(u'Entered text'),
            _(u'Created'),
            ])

        for answer in self.answers:
            # user
            user = answer.voter.user
            user_id = '' if user is None else user.id
            full_name = '' if user is None else user.get_profile().get_full_name()

            self.writer.writerow([
                answer.id,
                answer.voter.id,
                user_id,
                full_name,
                answer.custom,
                answer.created.astimezone(self.tz)
            ])

    def export(self):
        self.count_answers()
        self.write_header()
        self.write_customs()
#        self.write_answers()
        return super(TextQuestionCsvHandler, self).export()

