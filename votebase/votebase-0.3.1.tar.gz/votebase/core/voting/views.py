import datetime

from django.contrib import messages
from django.contrib.gis.geoip import GeoIP
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.dateparse import parse_datetime
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormView

from votebase.core.questions.models import Question
from votebase.core.surveys.models import Round
from votebase.core.utils import mail
from votebase.core.voting.forms import PasswordForm
from votebase.core.voting.models import Voter, VotedQuestion


def get_password_ident(round):
    return 'password_%s' % round.pk


def get_welcome_ident(round):
    return 'welcome_%s' % round.pk


def get_questions_ident(round):
    return 'questions_%s' % round.pk


def get_voting_started_ident(round):
    return 'voting_started_%s' % round.pk


class VoteView(TemplateResponseMixin, View):
    template_name = 'voting/vote.html'

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk', ))
        self.survey = self.round.survey

        # Inactive segment
        if not self.is_active():
            return redirect(reverse('voting_inactive', args=(self.round.pk, )))

        # Permission restriction
        if self.round.permission_level == Round.PERMISSION_LEVEL_REGISTERED and not request.user.is_authenticated():
            return redirect(reverse('voting_for_registered', args=(self.round.pk, )))

        # Repeatable voting
        if not self.round.is_repeatable and self.already_voted(request.user, self.round):
            return redirect(reverse('voting_already_voted', args=(self.round.pk, )))

        # Secured by password
        if get_password_ident(self.round) not in request.session:
            if self.round.is_secured():
                return redirect(reverse('voting_password', args=(self.round.pk, )))

        # Chaining
        if 'ancestor_child' in request.session:
            # Redirected from previous ancestor finish view
            del request.session['ancestor_child']

        # Check if it is child segment
        if self.round.ancestor is None:
            # it is not child
            request.session['current_round'] = self.round.pk
        else:
            # In media res (jumping directly to child voting URL)
            if request.user.is_authenticated():
                # Logged in user
                voters = Voter.objects.filter(round=self.round.ancestor, user=request.user)
                if not voters.count():
                    # User hasn't voted in ancestor segment yet
                    request.session['ancestor_child'] = self.round.pk
                    request.session['current_round'] = self.round.ancestor.pk
                    return redirect(reverse('voting_vote', args=(self.round.ancestor.pk, )))
            else:
                # Anonymous user
                request.session['ancestor_child'] = self.round.pk
                if request.session.get('current_round', None) != self.round.pk:
                    request.session['current_round'] = self.round.ancestor.pk
                    return redirect(reverse('voting_vote', args=(self.round.ancestor.pk, )))

        if 'current_round' in request.session:
            if request.session['current_round'] != self.round.pk:
                return redirect(reverse('voting_vote', args=(request.session['current_round'], )))

        # TODO: IMPLEMENT CORRECT CHAINING!!! This is temporary solution.
        # Selecting first ancestor child -> should choose exact one
        ancestor_childs = Round.objects.filter(ancestor=self.round)
        if ancestor_childs.exists():
            request.session['ancestor_child'] = ancestor_childs[0].pk

        # Skipping welcome screen
        if get_welcome_ident(self.round) not in request.session:
            if not self.should_skip_welcome():
                return redirect(reverse('voting_welcome',
                    args=(self.round.pk, )))

        self.questions = self.get_questions(request)

        # set voting start time
        if get_voting_started_ident(self.round) not in request.session:
            request.session[get_voting_started_ident(self.round)] = str(now())

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.survey.title, ''),
        ])

        return super(VoteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return self.render_to_response({
            'round': self.round,
            'survey': self.survey,
            'question_forms': [question.get_voting_form(number=index + 1) for index, question in enumerate(self.questions)],
        })

    def post(self, request, pk):
        is_valid = True
        forms = []

        # Validate all forms
        for index, question in enumerate(self.questions):
            form = question.get_voting_form(request.POST, number=index + 1)
            if not form.is_valid():
                is_valid = False
            forms.append(form)

        if is_valid:
            messages.success(request, _(u'Your votes has been successfully saved.'))

            # Geolocation
            g = GeoIP()
            location = g.city(request.META['REMOTE_ADDR']) or {}

            # get voting time details
            if get_voting_started_ident(self.round) in request.session:
                voting_started_str = request.session[get_voting_started_ident(self.round)]
                voting_started = parse_datetime(voting_started_str)
                voting_ended = now()
                voting_duration = (voting_ended - voting_started).seconds
                del request.session[get_voting_started_ident(self.round)]
            else:
                voting_started = None
                voting_ended = None
                voting_duration = None

            # Create voter
            voter = Voter.objects.create(
                ip_address=request.META['REMOTE_ADDR'],
                survey=self.survey,
                round=self.round,
                latitude=location.get('latitude', None),
                longitude=location.get('longitude', None),
                continent_code=location.get('continent_code', None),
                country_name=location.get('country_name', None),
                country_code=location.get('country_code', None),
                city=location.get('city', None),
                area_code=location.get('area_code', None),
                voting_started=voting_started,
                voting_ended=voting_ended,
                voting_duration=voting_duration
            )

            if request.user.is_authenticated():
                voter.user = request.user
                voter.save()

            # Save all forms
            for form in forms:
                form.save(voter)

            # Save voted questions list of voter
            for index, question in enumerate(self.questions):
                VotedQuestion.objects.create(
                    voter=voter,
                    question=question,
                    weight=index,
#                    page=1,
                )

            # Save voter quiz result
            if self.survey.is_quiz():
                voter.quiz_result = voter.get_quiz_result()
                voter.save()

                # Send email with quiz results to voter if permitted
                if self.round.is_quiz_result_visible and voter:
                    if voter.user:
                        self.send_quiz_result_to_voter(voter)

            # Send email about new voter if necessary
            try:
                if not self.round.voter_set.count() % self.round.email_treshold:
                    mail.new_voters(self.round, request)
            except ZeroDivisionError:
                pass

            request.session['voter'] = voter.pk

            return redirect(reverse('voting_finish', args=(self.round.pk, )))
        else:
            messages.error(request, _(u'Make sure that you have answered all required questions.'))

        return self.render_to_response({
            'round': self.round,
            'survey': self.survey,
            'question_forms': forms,
        })

    def get_questions(self, request):
        if self.round.count_questions is not None and\
           self.round.count_questions != self.survey.question_set.count():

            if get_questions_ident(self.round) in request.session:
                questions_pks = request.session[get_questions_ident(self.round)]
                questions = Question.objects.filter(pk__in=questions_pks)
            else:
                questions = self.round.get_random_questions()
                request.session[get_questions_ident(self.round)] = list(questions.values_list('pk', flat=True))
        else:
            questions = self.survey.question_set.all().prefetch_related('option_set')

        return questions.order_by('weight')

    def is_active(self):
        if not self.round.is_active:
            return False

        if not self.round.is_date_in_range():
            return False

        return True

    def already_voted(self, user, round):
        if not user.is_authenticated():
            return False

        return Voter.objects.filter(user=user, round=round).count()

    def should_skip_welcome(self):
#        if strip_tags(self.survey.preface) in EMPTY_VALUES:
#            return True
#
#        return False
        return True

    def send_quiz_result_to_voter(self, voter):
        voter.send_quiz_result()


class InactiveView(TemplateResponseMixin, View):
    template_name = 'voting/inactive.html'

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.survey = self.round.survey

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.survey.title, ''),
        ])

        return super(InactiveView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return self.render_to_response({
            'survey': self.round.survey,
            'round': self.survey,
            })


class OnlyForRegisteredView(TemplateResponseMixin, View):
    template_name = 'voting/only_for_registered.html'

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.survey = self.round.survey

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.survey.title, ''),
        ])

        return super(OnlyForRegisteredView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return self.render_to_response({
            'survey': self.round.survey,
            'round': self.survey,
            })


class AlreadyVotedView(TemplateResponseMixin, View):
    template_name = 'voting/already_voted.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.survey = self.round.survey

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.survey.title, ''),
        ])

        return super(AlreadyVotedView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        voters = Voter.objects.filter(round=self.round, user=request.user)

        return self.render_to_response({
            'survey': self.round.survey,
            'round': self.survey,
            'voters': voters
            })


class WelcomeView(TemplateResponseMixin, View):
    template_name = 'voting/welcome.html'

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.welcome_ident = get_welcome_ident(self.round)

        if self.welcome_ident in request.session:
            return redirect(reverse('voting_vote', args=(self.round.pk, )))

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.round.survey.title, ''),
        ])

        return super(WelcomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return self.render_to_response({
            'survey': self.round.survey,
            'round': self.round,
        })

    def post(self, request, pk):
        if self.welcome_ident not in request.session:
            request.session[self.welcome_ident] = True
        return redirect(reverse('voting_vote', args=(self.round.pk, )))


class PasswordView(FormView):
    template_name = 'voting/password.html'
    form_class = PasswordForm

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.password_ident = get_password_ident(self.round)

        if self.password_ident in request.session:
            return redirect(reverse('voting_vote', args=(self.round.pk, )))

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.round.survey.title, ''),
        ])

        return super(PasswordView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(PasswordView, self).get_context_data(**kwargs)
        context_data['survey'] = self.round.survey
        context_data['round'] = self.round
        return context_data

    def get_form_kwargs(self):
        form_kwargs = super(PasswordView, self).get_form_kwargs()
        form_kwargs['round'] = self.round
        return form_kwargs

    def get_success_url(self):
        return reverse('voting_vote', args=(self.round.pk, ))

    def form_valid(self, form):
        if self.password_ident not in self.request.session:
            self.request.session[self.password_ident] = True
        return super(PasswordView, self).form_valid(form)


class FinishView(TemplateView):
    template_name = 'voting/finish.html'

    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.voter = Voter.objects.get(pk=request.session['voter']) if 'voter' in request.session else None

        # Remove welcome session flag
        welcome_ident = get_welcome_ident(self.round)
        if welcome_ident in request.session:
            del request.session[welcome_ident]

        # Remove questions session flag
        questions_ident = get_questions_ident(self.round)
        if questions_ident in request.session:
            del request.session[questions_ident]

        if 'current_round' in request.session:
            del request.session['current_round']

        # Chaining
        if 'ancestor_child' in request.session:
            request.session['current_round'] = request.session['ancestor_child']

        # Redirect to voter results if survey is quiz
        #TODO: postface is hidden now, it should be displayed somewhere
        # if self.round.survey.is_quiz() and self.round.is_quiz_result_visible and self.voter:
        #     return redirect(self.voter.get_absolute_hash_url())

        request.breadcrumbs([
            (_(u'Voting'), reverse('voting_vote', args=(self.round.pk, ))),
            (self.round.survey.title, ''),
        ])
        return super(FinishView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FinishView, self).get_context_data(**kwargs)
        context['survey'] = self.round.survey
        context['round'] = self.round
        context['voter'] = self.voter
        return context
