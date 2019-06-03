from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.db.models.aggregates import Count, Avg
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.list import ListView

from votebase.core.questions.models import Question
from votebase.core.statistics.helpers import limit_answers
from votebase.core.surveys.models import Round, Survey
from votebase.core.utils.helpers import paginate, sorted_by_roman
from votebase.core.voting.models import Answer, VotedQuestion


class GraphsView(ListView):
    model = Question
    template_name = 'statistics/graphs.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = None

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(kwargs.get('pk'), ))),
        ])

        return super(GraphsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(GraphsView, self).get_queryset()
        queryset = queryset.filter(survey=self.survey)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GraphsView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        context['round'] = self.round
        if self.survey.is_quiz():
            context['statistics_categories'] = self.get_statistics_of_categories()
        context['show_export_pdf_btn'] = 'wkhtmltopdf' in settings.INSTALLED_APPS
        return context

    def categories_info(self, survey=None, segment=None):
        if not survey and not segment:
            raise ValueError('Neither survey nor segment specified')

        if not survey:
            survey = segment.survey

        # questions
        questions = Question.objects.filter(survey=survey)

        if segment:
            questions = questions.filter(survey__round=segment)

        # voted questions
        segment_voted_questions = VotedQuestion.objects.filter(question__survey=survey).exclude(voter__is_irrelevant=True)

        if segment:
            segment_voted_questions = segment_voted_questions.filter(question__survey__round=segment)

        categories = list(set(questions.order_by('weight').values_list('category', flat=True)))
        categories = sorted_by_roman(categories)

        categories_info = []

        for category in categories:
            num_questions = questions.filter(category=category).count()
            voted_questions = segment_voted_questions.filter(question__category=category)
            quiz_result = voted_questions.aggregate(Avg('quiz_result'))['quiz_result__avg']
            percent = quiz_result * 100 if quiz_result is not None else None

            categories_info.append({
                'category': category,
                'percent': percent,
                'count_questions': num_questions
            })

        return categories_info

    def get_statistics_of_categories(self):
        return self.categories_info(survey=self.survey, segment=self.round)

        # categories = list(set(self.get_queryset()\
        #     .exclude(category='')\
        #     .order_by('category')\
        #     .values_list('category', flat=True)))
        #
        # categories = sorted_by_roman(categories)
        #
        # categories_stats = self.get_queryset()\
        #     .exclude(category='')\
        #     .values('category')\
        #     .order_by('category')\
        #     .annotate(count=Count('category'))
        #
        # #        quiz_answers = Answer.objects.select_related('question', 'voter').filter(
        # quiz_answers = Answer.objects.filter(
        #     #                question__kind,=...
        #     question__survey=self.survey,
        #     question__is_quiz=True,
        #     voter__is_irrelevant=False,
        # )
        # if self.round:
        #     quiz_answers = quiz_answers.filter(voter__round=self.round)
        #
        # # TODO: better sorting algorithm
        # for category_title in categories:
        #     for category_stat in categories_stats:
        #         category = category_stat['category']
        #
        #         if category == category_title:
        #             count_questions = category_stat['count']
        #             c_answers = quiz_answers.filter(question__category=category)
        #             c_correct_answers = c_answers.filter(option__is_correct=True)
        #
        #             correct_answers_count = c_correct_answers.count()
        #             answers_count = c_answers.count()
        #
        #             try:
        #                 percent = float(correct_answers_count) * 100 / answers_count
        #             except ZeroDivisionError:
        #                 percent = 0
        #
        #             cstats.append({
        #                 'category': category,
        #                 'count_questions': count_questions,
        #                 'correct_answers': correct_answers_count,
        #                 'answers': answers_count,
        #                 'percent': percent
        #             })
        return cstats


class GraphsHashView(GraphsView):
    template_name = 'statistics/graphs_hash.html'

    def dispatch(self, request, *args, **kwargs):
        self.set_survey_and_round(kwargs)

        if not self.survey:
            raise Http404('No %s matches the given query.' % Survey._meta.object_name)

        request.breadcrumbs([
            (self.survey.title, '#'),
        ])

        return super(GraphsView, self).dispatch(request, *args, **kwargs)

    def set_survey_and_round(self, kwargs):
        if 'round_hash_key' in kwargs:
            self.round = get_object_or_404(Round, hash_key=kwargs.get('round_hash_key'))
            self.survey = self.round.survey
        elif 'survey_hash_key' in kwargs:
            self.survey = get_object_or_404(Survey, hash_key=kwargs.get('survey_hash_key'))
            self.round = None
        else:
            self.survey = None
            self.round = None


class GraphMixin(object):
    def is_need_to_check_ownership(self, request, survey, round):
        try:
            if survey.hash_key not in EMPTY_VALUES and\
               survey.hash_key in request.META['HTTP_REFERER']:
                return False
            if round is not None and round.hash_key not in EMPTY_VALUES and\
               round.hash_key in request.META['HTTP_REFERER']:
               return False
        except KeyError:
            return True
        return True


class GraphOptionsQuestionView(GraphMixin, TemplateResponseMixin, View):
    template_name = 'statistics/graphs/options.html'

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

        # set option information
        self.max_percent = 0
        self.options = []
        for option in self.question.option_set.all():
            answers = self.all_answers.filter(option=option)
            count = answers.count()

            try:
#                percent = count * 100 / max_answers_per_option
                percent = count * 100 / self.total_answers_count
            except ZeroDivisionError:
                percent = 0
            percent = round(percent, 2)

            if percent > self.max_percent:
                self.max_percent = percent

            self.options.append({
                'is_correct': option.is_correct,
                'title': option.get_image_title(),
                'count': answers.count(),
                'percent': percent
            })

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(self.survey.id, ))),
            (_(u'Survey questions'), reverse('statistics_graphs', args=(self.survey.id, ))),
        ])

        return super(GraphOptionsQuestionView, self).dispatch(request, *args, **kwargs)

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
            'options': self.options,
            'max_percent': self.max_percent,
            'total_answers': self.total_answers_count,
            'export_url': self.get_export_url(),
            'is_public_view': self.is_public_view
        })


class GraphTextvalueView(GraphMixin, TemplateResponseMixin, View):
    template_name = 'statistics/graphs/options.html'

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

        # order by count
        answers = self.all_answers.values('custom').annotate(count=Count('pk')).order_by('-count')

        # find most repeating custom answer
#        most_custom = answers[0]
#        max_count = most_custom['count']

        # set option information
        self.max_percent = 0
        self.customs = []
        for answer in answers:
            count = answer['count']

            try:
#                percent = count * 100 / max_count
                percent = float(count) * 100 / self.total_answers_count
            except ZeroDivisionError:
                percent = 0
            percent = round(percent, 2)

            if percent > self.max_percent:
                self.max_percent = percent

            self.customs.append({
                'title': answer['custom'],
                'count': count,
                'percent': percent
            })

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(self.survey.id, ))),
            (_(u'Survey questions'), reverse('statistics_graphs', args=(self.survey.id, ))),
        ])

        return super(GraphTextvalueView, self).dispatch(request, *args, **kwargs)

    def get_export_url(self):
        if self.round is not None:
            return reverse('statistics_export_round',
                args=(self.question.id, self.round.id))

        return reverse('statistics_export', args=(self.question.id,))

    def get(self, request, pk, round_pk = None):
        pagination = paginate(self.request, self.customs)

        return self.render_to_response({
            'pagination': pagination,
            'survey': self.survey,
            'round': self.round,
            'question': self.question,
#            'options': self.customs,
            'max_percent': self.max_percent,
            'options': pagination['object_list'],
            'total_answers': self.total_answers_count,
            'export_url': self.get_export_url(),
            'is_public_view': self.is_public_view
            })
