from datetime import datetime, timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.db import models
from django.db.models import DateField
from django.db.models.aggregates import Count, Avg
from django.db.models.functions import Cast
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView

from votebase.core.accounts.helpers import get_profile_model
from votebase.core.statistics.helpers import limit_voters
from votebase.core.surveys.models import Round, Survey
from votebase.core.voting.models import Voter


class InfographicsView(ListView):
    model = Voter
    template_name = 'statistics/infographics.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = None

        #        self.all_voters = limit_voters(self.get_queryset(), self.survey)

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(kwargs.get('pk'), ))),
        ])

        # package restriction
        self.all_voters = limit_voters(self.get_queryset(), self.survey)

        # total count
        self.total_voters_count = self.all_voters.count()

        return super(InfographicsView, self).dispatch(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        if self.round is not None:
            qs = queryset.filter(round=self.round)
        else:
            qs = queryset.filter(round__survey=self.survey)

        return qs.filter(is_irrelevant=False)

    def get_queryset(self):
        queryset = super(InfographicsView, self).get_queryset()
        queryset = self.filter_queryset(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(InfographicsView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        context['round'] = self.round
        context['show_export_pdf_btn'] = 'wkhtmltopdf' in settings.INSTALLED_APPS
        context['data_age'] = self.get_data_age()
        context['data_gender'] = self.get_data_gender()
        context['data_voters'] = self.get_data_voters()
        context['data_voters_total'] = self.get_data_voters_total(context['data_voters'])
        context['data_voting_duration'] = self.get_data_voting_duration()
        if self.survey.is_quiz():
            context['data_quiz_result'] = self.get_data_quiz_result()
            context['data_quiz_result_by_age'] = self.get_data_quiz_result_by_age()
        return context

    def get_data_quiz_result_by_age(self):
        profile_model = get_profile_model()

        if hasattr(profile_model, 'age'):
            return self.get_data_quiz_result_by_age__age_field()

        if hasattr(profile_model, 'date_of_birth'):
            return self.get_data_quiz_result_by_age__dob()

        return []

    def get_data_quiz_result_by_age__age_field(self):
        profile_model = get_profile_model()

        def calculate(field_path):
            result_path = 'quiz_result'
            my_filter=dict()
            my_filter['%s__isnull' % result_path] = True
            my_filter['%s__isnull' % field_path] = True

            return self.all_voters\
                .exclude(user__isnull=True)\
                .exclude(**my_filter)\
                .order_by(field_path)\
                .values(field_path)\
                .annotate(average_result=Avg(result_path))

        try:
            field_path = 'user__profile__age'
            voters = calculate(field_path)
        except FieldError:
            field_path = 'user__profile__%s__age' % str(profile_model.__name__).lower()
            voters = calculate(field_path)

        data = []
        try:
            for voter in voters:
                data.append({
                    'age': voter[field_path],
                    'average_result': voter['average_result']
                })
        except ValueError:
            pass
        return data

    def get_data_quiz_result_by_age__dob(self):
        result_path = 'quiz_result'

        def calculate(field_path):
            my_filter=dict()
            my_filter['%s__isnull' % result_path] = True
            my_filter['%s__isnull' % field_path] = True

            return self.all_voters\
            .exclude(user__isnull=True)\
            .exclude(**my_filter)\
            .order_by(field_path)\
            .values(field_path, result_path)

        field_path = 'user__profile__date_of_birth'
        voters = calculate(field_path)

        results = dict()
        for voter in voters:
            date = voter[field_path]
            if date in EMPTY_VALUES:
                continue
            age = (now().date() - date).days/365
            quiz_result = voter[result_path]
            if not age in results:
                results[age] = {
                    'count': 1,
                    'sum': quiz_result,
                    'avg': quiz_result
                }
            else:
                old_count = results[age]['count']
                new_count = old_count+1
                old_sum = results[age]['sum']
                new_sum = old_sum + quiz_result
                new_avg = new_sum/new_count
                results[age] = {
                    'count': new_count,
                    'sum': new_sum,
                    'avg': new_avg
                }

        data = []
        try:
            for age in results:
                data.append({
                    'age': age,
                    'average_result': results[age]['avg']
                })
        except ValueError:
            pass

        return data

    def get_data_quiz_result(self):
        field_path = 'quiz_result'
        my_filter=dict()
        my_filter['%s__isnull' % field_path] = True

        voters = self.all_voters\
            .exclude(**my_filter)\
            .values(field_path)\
            .annotate(count=Count(field_path))\
            .order_by(field_path)

        data = []

        try:
            for voter in voters:
                data.append({
                    'quiz_result': str(voter[field_path]),
                    'count': voter['count']
                })
        except ValueError:
            pass
        return data

    def get_data_voting_duration(self):
        field_path = 'voting_duration'
        my_filter = dict()
        my_filter['%s__isnull' % field_path] = True

        voters = self.all_voters\
            .exclude(**my_filter)\
            .extra(select={field_path: '%s/60' % field_path,})\
            .values(field_path)\
            .annotate(count=Count(field_path))\
            .order_by(field_path)

        data = []

        try:
            for voter in voters:
                data.append({
                    'duration': str(voter[field_path]),
                    'count': voter['count']
                })
        except ValueError:
            pass
        return data

    def get_data_voters(self):
        field_name = 'created'
        new_field_name = '{}_date'.format(field_name)

        voters = self.all_voters \
            .annotate(**{new_field_name: Cast(field_name, DateField())}) \
            .values(new_field_name)\
            .annotate(count=Count(new_field_name))\
            .order_by(new_field_name)

        data = []
        try:
            for voter in voters:
                data.append({
                    'date': str(voter[new_field_name]),
                    'count': voter['count'],
                })
        except ValueError:
            pass
        return data

    def get_data_voters_total(self, data_voters):
        data = []

        try:
            for d in data_voters:
                created_datetime = datetime.strptime(d['date'], '%Y-%m-%d')+timedelta(days=1)
                count_total = self.all_voters.filter(created__lte=created_datetime).count()

                data.append({
                    'date': d['date'],
                    'count': count_total,
                    })
        except ValueError:
            pass
        return data

    def get_data_gender(self):
        profile_model = get_profile_model()

        if not hasattr(profile_model, 'gender'):
            return []

        field_path = 'user__profile__gender'

        genders_registered = self.all_voters\
            .values(field_path).annotate(count=Count(field_path))\
            .order_by(field_path)

        genders_anonymous = self.all_voters.filter(user__isnull=True)

        data = []

        try:
            for gender in genders_registered:
                label_value = gender[field_path]
                count = gender['count']

                if label_value == 'm':
                    label = _(u'Male')
                elif label_value == 'f':
                    label = _(u'Female')
                else:
                    label = _(u'Unknown')
                    count += genders_anonymous.count()

                data.append({
                    'label': label,
                    'count': count
                })

        except ValueError:
            pass
        return data

    def get_data_age(self):
        profile_model = get_profile_model()

        if hasattr(profile_model, 'age'):
            return self.get_data_age_by_age()

        if hasattr(profile_model, 'date_of_birth'):
            return self.get_data_age_by_dob()

        return []

    def get_data_age_by_age(self):
        profile_model = get_profile_model()

        def calculate(field_path):
            my_filter = dict()
            my_filter['%s__isnull' % field_path] = True

            return self.all_voters\
                .exclude(user__isnull=True)\
                .exclude(**my_filter)\
                .values(field_path).annotate(count=Count(field_path))\
                .order_by(field_path)

        try:
            field_path = 'user__profile__age'
            ages = calculate(field_path)
        except FieldError:
            field_path = 'user__profile__%s__age' % str(profile_model.__name__).lower()
            ages = calculate(field_path)

        data = []
        try:
            for age in ages:
                data.append({
                    'age': age[field_path],
                    'count': age['count']
                })
        except ValueError:
            pass
        return data

    def get_data_age_by_dob(self):
        dates_of_birth = self.all_voters\
        .exclude(user__isnull=True)\
        .exclude(user__profile__date_of_birth__isnull=True)\
        .values_list('user__profile__date_of_birth', flat=True)\
        .order_by('-user__profile__date_of_birth')

        ages = []
        for date_of_birth in dates_of_birth:
            ages.append((now().date() - date_of_birth).days/365)

        data = []
        try:
            age_min = min(ages)
            age_max = max(ages)
            for age in range(max(age_min-10, 0), age_max+10):
                data.append({
                    'age': age,
                    'count': ages.count(age)
                })
        except ValueError:
            pass
        return data


class InfographicsHashView(InfographicsView):
    model = Voter
    template_name = 'statistics/infographics_hash.html'

    def dispatch(self, request, *args, **kwargs):
        self.set_survey_and_round(kwargs)

        if not self.survey:
            raise Http404('No %s matches the given query.' % Survey._meta.object_name)

        self.all_voters = limit_voters(self.get_queryset(), self.survey)

        # package restriction
        self.all_voters = limit_voters(self.all_voters, self.survey)

        # total count
        self.total_voters_count = self.all_voters.count()

        request.breadcrumbs([
            (self.survey.title, '#'),
        ])

        return super(InfographicsView, self).dispatch(request, *args, **kwargs)

    def set_survey_and_round(self, kwargs):
        if 'round_hash_key' in kwargs:
            self.round = get_object_or_404(Round, hash_key=kwargs.get('round_hash_key'))
            self.survey = self.round.survey
        elif 'survey_hash_key' in kwargs:
            self.survey = get_object_or_404(Survey, hash_key=kwargs.get('survey_hash_key'))
            self.round = None
        else:
            self.round = None
            self.round = None
