from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView

from votebase.core.questions.forms.thumbs import ThumbsForm
from votebase.core.questions.models import Question, Option
from votebase.core.surveys.models import Survey


class ThumbsCreateView(CreateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = ThumbsForm
    kind = Question.KIND_THUMBS

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(ThumbsCreateView, self).dispatch(request, *args,
            **kwargs)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.survey = self.survey
        self.object.kind = self.kind
        self.object.save()

        Option.objects.create(
            title=0,
            question=self.object
        )

        Option.objects.create(
            title=1,
            question=self.object
        )

        messages.success(self.request, _(u'Question successfully created.'))

        return super(ThumbsCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ThumbsCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create rating thumbs')
        context['content_title'] = _(u'Create rating thumbs')
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['kind'] = self.kind
        action_url = 'questions_create_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.survey.pk,))
        return context

class ThumbsUpdateView(UpdateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = ThumbsForm
    kind = Question.KIND_THUMBS

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(ThumbsUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(ThumbsUpdateView, self).get_form(form_class)
        form.fields['image'].widget.attrs['remove_url'] =\
        reverse('questions_delete_image', args=(self.question.pk, ))
        return form

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u'Question successfully updated.'))
        return super(ThumbsUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))


    def get_context_data(self, **kwargs):
        context = super(ThumbsUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update rating thumbs')
        context['content_title'] = _(u'Update rating thumbs')
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['kind'] = self.kind
        action_url = 'questions_update_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.question.pk,))
        return context
