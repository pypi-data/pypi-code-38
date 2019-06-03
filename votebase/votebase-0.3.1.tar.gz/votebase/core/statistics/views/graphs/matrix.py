from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateResponseMixin

from votebase.core.questions.models import Question
from votebase.core.statistics.helpers import limit_answers
from votebase.core.statistics.views.graphs.general import GraphMixin
from votebase.core.surveys.models import Round
from votebase.core.voting.models import Answer


class GraphMatrixView(GraphMixin, TemplateResponseMixin, View):
    template_name = 'statistics/graphs/matrix.html'

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
            self.all_answers = Answer.objects.filter(question=self.question, voter__round=self.round).distinct()
        else:
            self.round = None
            self.all_answers = Answer.objects.filter(question=self.question).distinct()

        # filter irrelevant voters
        self.all_answers = self.all_answers.filter(voter__is_irrelevant=False)

        # check if hash key is in HTTP referer
        # (ajax request for public statistics URL)
        if self.is_need_to_check_ownership(request, self.survey, self.round):
            self.is_public_view = False
            if self.survey.user != request.user:
                return HttpResponseForbidden()
        else:
            self.is_public_view = True

        # package restriction
        self.all_answers = limit_answers(self.all_answers, self.survey)

        # total count
        self.total_answers_count = self.all_answers.count()

        # find maximum answers per option
#        max_answers_per_option = self.all_answers.values('option').annotate(count=Count('option__pk')).order_by('-count')[0]['count']

        # set row information
        self.options_rows = self.question.option_set.all().orientation_row()
        self.options_columns = self.question.option_set.all().orientation_column()

        self.rows=[]
        self.max_percent = 0
        for option_row in self.options_rows:
            columns = []

            for option_column in self.options_columns:
                answers = self.all_answers.filter(option=option_row, option_column=option_column)
                count = answers.count()

                try:
#                    percent = count * 100 / max_answers_per_option
                    percent = count * 100 / self.total_answers_count
                except ZeroDivisionError:
                    percent = 0

                if percent > self.max_percent:
                    self.max_percent = percent

                columns.append({
                    'count': answers.count(),
                    'percent': percent
                })

            self.rows.append({
                'title': option_row.get_image_title(),
                'columns': columns
            })

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(self.survey.pk, ))),
            (_(u'Survey questions'), reverse('statistics_graphs', args=(self.survey.id, ))),
        ])

        return super(GraphMatrixView, self).dispatch(request, *args, **kwargs)

    def get_export_url(self):
        if self.round is not None:
            return reverse('statistics_export_round',
                args=(self.question.id, self.round.id))

        return reverse('statistics_export', args=(self.question.id,))

    def get(self, request, pk, round_pk = None):
        return self.render_to_response({
            'survey': self.survey,
            'round': self.round,
            'question': self.question,
            'rows': self.rows,
            'columns': self.options_columns,
            'max_percent': self.max_percent,
            'total_answers': self.total_answers_count,
            'export_url': self.get_export_url(),
            'is_public_view': self.is_public_view
            })