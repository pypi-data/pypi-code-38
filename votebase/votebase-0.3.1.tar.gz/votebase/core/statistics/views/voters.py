from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.list import ListView

from votebase.core.questions.models import Question
from votebase.core.statistics.forms import VoterFlagForm
from votebase.core.surveys.models import Survey, Round
from votebase.core.utils.helpers import paginate
from votebase.core.voting.models import Voter, VotedQuestion


class VotersView(ListView):
    model = Voter
    template_name = 'statistics/voters.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = self.survey.get_last_round()

        #generate quiz results if necessary
#        if self.survey.is_quiz():
#            voters_to_fix = self.get_queryset().filter(quiz_result=None)
#            print len(voters_to_fix)
#            for voter in voters_to_fix:
#                voter.quiz_result = voter.get_quiz_result()
#                voter.save()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index',
                args=(kwargs.get('pk'), ))),
        ])

        return super(VotersView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        voters_limit = self.request.user.get_profile().get_voters_limit()
        queryset = super(VotersView, self).get_queryset()
        queryset = queryset.filter(round=self.round)[:voters_limit]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VotersView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        context['survey_is_quiz'] = self.survey.is_quiz()
        context['round'] = self.round

        pagination = paginate(self.request, self.get_queryset().all())
        context['pagination'] = pagination
        context['object_list'] = pagination['object_list']

        return context


class VoterView(TemplateResponseMixin, View):
    template_name = 'statistics/voter.html'

    def dispatch(self, request, *args, **kwargs):
        self.voter = get_object_or_404(Voter, pk=kwargs.get('pk', ))
        self.round = self.voter.round
        self.survey = self.round.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
            (_(u'Voters'), reverse('statistics_voters',
                args=(self.survey.pk, ))),
        ])

        self.show_quiz_result = True          # only survey creator can see this view
        self.show_quiz_correct_options = True # only survey creator can see this view
        return super(VoterView, self).dispatch(request, *args, **kwargs)

    def get_voter_forms(self, voter):
        # Get list of voted questions
        voter_questions = VotedQuestion.objects.get_voter_questions(voter)

        forms = []
        for index, question in enumerate(voter_questions):
            if question.is_quiz:
                forms.append(
                    question.get_voter_form(
                        voter,
                        number=(index + 1),
                        show_quiz_correct_options=self.show_quiz_correct_options)
                )
            else:
                forms.append(
                    question.get_voter_form(
                        voter,
                        number=(index + 1))
                )

        return forms

    def get_context_data(self):
        # Get list of voted questions
        use_cache = getattr(settings, 'VOTEBASE_USE_VOTER_FORM_CACHE', True)
        forms = cache.get('voter_forms', version=self.voter.pk)

        if not forms or not use_cache:
            forms = self.get_voter_forms(self.voter)
            cache.set('voter_forms', forms, version=self.voter.pk, timeout=60*60*12)

        return {
            'voter': self.voter,
            'survey': self.survey,
            'forms': forms,
            'show_quiz_result': self.show_quiz_result,
            'show_quiz_correct_options': self.show_quiz_correct_options
        }

    def get(self, request, pk):
        return self.render_to_response(self.get_context_data())


class VoterByHashView(VoterView):
    template_name = 'statistics/voter_hash.html'

    def dispatch(self, request, *args, **kwargs):
        self.voter = get_object_or_404(Voter, hash_key=kwargs.get('hash_key', ))
        self.round = self.voter.round
        self.survey = self.round.survey

        # Get list of voted questions
        self.questions = VotedQuestion.objects.get_voter_questions(self.voter)

        if self.voter.user:
            self.back_url = reverse('voting_already_voted', args=(self.round.pk, ))
        else:
            self.back_url = reverse('voting_finish', args=(self.round.pk, ))

        request.breadcrumbs([
            (self.survey.title, self.back_url),
        ])

        self.show_quiz_result = self.is_quiz_result_visible(request.user)
        self.show_quiz_correct_options = self.is_quiz_correct_options_visible(request.user)

        self.request = request

        return self.get(request, None)

    def get_context_data(self):
        data = super(VoterByHashView, self).get_context_data()
        data['back_url'] = self.back_url
        return data

    def is_quiz_result_visible(self, user):
        is_quiz_result_visible = self.round.is_quiz_result_visible

#        is_logged_in = user.is_authenticated()
#        is_creator = is_logged_in and user == self.round.survey.user
#
#        if is_creator:
#            return True

        return is_quiz_result_visible

    def is_quiz_correct_options_visible(self, user):
        is_quiz_correct_options_visible = self.round.is_quiz_correct_options_visible

        #        is_logged_in = user.is_authenticated()
        #        is_creator = is_logged_in and user == self.round.survey.user
        #
        #        if is_creator:
        #            return True

        return is_quiz_correct_options_visible


class VoterUpdateView(UpdateView):
    model = Voter
    form_class = VoterFlagForm
    template_name = 'statistics/voter_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.voter = get_object_or_404(Voter, pk=kwargs.get('pk', None))

        if self.voter.round.survey.user != request.user:
            return HttpResponseForbidden()

        self.round = self.voter.round
        self.survey = self.round.survey

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index',
                args=(self.survey.pk, ))),
            (_(u'Voters'), reverse('statistics_voters',
                args=(self.survey.pk, ))),
        ])

        return super(VoterUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(VoterUpdateView, self).get_context_data(**kwargs)
        context_data['survey'] = self.survey
        return context_data

    def get_success_url(self):
        return reverse('statistics_voters', args=(self.survey.pk, ))


class VoterHistoryView(VoterByHashView):
    template_name = 'statistics/voter_hash.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.voter = get_object_or_404(Voter, hash_key=kwargs.get('hash_key', ))

        if self.voter.user != request.user:
            return HttpResponseForbidden()

        self.round = self.voter.round
        self.survey = self.round.survey

        # Get list of voted questions
        self.questions = VotedQuestion.objects.get_voter_questions(self.voter)
        self.back_url = reverse('statistics_voting_history')

        request.breadcrumbs([
            (self.survey.title, self.back_url),
        ])

        self.show_quiz_result = self.is_quiz_result_visible(request.user)
        self.show_quiz_correct_options = self.is_quiz_correct_options_visible(request.user)

        self.request = request

        return self.get(request, None)


class VotingHistory(ListView):
    model = Voter
    template_name = 'statistics/voting_history.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Profile'), reverse('accounts_profile')),
        ])

        return super(VotingHistory, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(VotingHistory, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VotingHistory, self).get_context_data(**kwargs)
        pagination = paginate(self.request, self.get_queryset().all())
        context['pagination'] = pagination
        context['object_list'] = pagination['object_list']
        return context


class VoterDeleteView(View):
    success_url = 'statistics_voters'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        voter = get_object_or_404(Voter, pk=kwargs.get('pk'))
        survey = voter.survey

        if survey.user != request.user:
            return HttpResponseForbidden()

        voter.delete()

        messages.success(request, _(u'Voter successfully deleted.'))

        return redirect(reverse(self.success_url, args=(survey.pk,)))


class VotersNonQuizResults(View):
#    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('password') != 'houdini':
            return HttpResponseForbidden()
    #        if not request.user.is_superuser:
    #            return HttpResponseForbidden()

        quiz_questions = Question.objects.filter(is_quiz=True).order_by('survey')
        quiz_surveys = quiz_questions.values_list('survey_id', flat=True).distinct()
        voters = Voter.objects.filter(quiz_result=None, survey_id__in=quiz_surveys)
        html = u'Voters to fix: %d' % len(voters)
        return HttpResponse(html)


class GenerateQuizResults(View):
#    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('password') != 'houdini':
            return HttpResponseForbidden()

#        if not request.user.is_superuser:
#            return HttpResponseForbidden()

        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        voters = Voter.objects.filter(quiz_result=None)
        print 'non result voters: %d' % len(voters)
        quiz_questions = Question.objects.filter(is_quiz=True).order_by('survey')
        print 'quiz questions: %d' % len(quiz_questions)
        quiz_surveys = quiz_questions.values_list('survey_id', flat=True).distinct()
        print 'quiz surveys: %d' % len(quiz_surveys)
        pp.pprint(quiz_surveys)
#        for s in quiz_surveys:
#            print s

        voters = Voter.objects.filter(survey_id__in=quiz_surveys)
        print 'quiz survey voters: %d' % len(voters)

        voters = voters.filter(quiz_result=None)
        print 'quiz survey non result voters: %d' % len(voters)

        debug_voters = Voter.objects.filter(quiz_result=None, survey_id__in=quiz_surveys)
        print 'debug_voters: %d' % len(debug_voters)

        count = 0
        for voter in debug_voters:
            count += 1
            voter.quiz_result = voter.get_quiz_result()
            voter.save()

        html = u'Voter quiz results successfuly generated (%d)' % count
        return HttpResponse(html)


class PreGenerateQuizResults(View):
#    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('password') != 'houdini':
            return HttpResponseForbidden()

        round_id = kwargs.get('round_pk')
        #        if not request.user.is_superuser:
        #            return HttpResponseForbidden()
        round = Round.objects.get(pk=round_id)

        if not round.survey.is_quiz():
            print u'survey %s is not quiz' % round.survey.title
            html = u'survey %s is not quiz' % round.survey.title
            return HttpResponse(html)

        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        voters = Voter.objects.filter(round_id=round_id)
        print 'voters to pregenerate: %d' % len(voters)

        count = 0
        for voter in voters:
            count+=1
            voter.quiz_result = voter.get_quiz_result()
            voter.save()

        html = u'Voter quiz results successfuly pregenerated (%d)' % count
        return HttpResponse(html)
