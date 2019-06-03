from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView

from votebase.core.questions.forms.textfield import TextfieldForm
from votebase.core.questions.models import Question
from votebase.core.surveys.models import Survey


class TextfieldCreateView(CreateView):
    template_name = 'questions/helpers/form.html'
    model = Question
    form_class = TextfieldForm
    success_url = 'questions_index'
    kind = Question.KIND_TEXTFIELD

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(TextfieldCreateView, self).dispatch(request, *args,
            **kwargs)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.survey = self.survey
        self.object.kind = self.kind
        self.object.save()

        messages.success(self.request, _(u'Question successfully created.'))

        return super(TextfieldCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TextfieldCreateView, self).get_context_data(**kwargs)
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['title'] = _(u'Create textfield')
        context['content_title'] = _(u'Create textfield')
        action_url = 'questions_create_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.survey.pk,))
        context['kind'] = self.kind
        return context


class TextfieldUpdateView(UpdateView):
    template_name = 'questions/helpers/form.html'
    model = Question
    form_class = TextfieldForm
    success_url = 'questions_index'
    kind = Question.KIND_TEXTFIELD

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(TextfieldUpdateView, self).dispatch(request, *args,
            **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _(u'Question successfully updated.'))
        return super(TextfieldUpdateView, self).form_valid(form)

    def get_form(self, form_class=None):
        form = super(TextfieldUpdateView, self).get_form(form_class)

        if 'image' in form.fields:
            form.fields['image'].widget.attrs['remove_url'] =\
            reverse('questions_delete_image', args=(self.question.pk, ))
        return form

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))

    def get_context_data(self, **kwargs):
        context = super(TextfieldUpdateView, self).get_context_data(**kwargs)
        context['submit_label'] = _(u'Done')
        context['title'] = _(u'Update textfield')
        context['content_title'] = _(u'Update textfield')
        action_url = 'questions_update_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.question.pk,))
        context['survey'] = self.survey
        context['kind'] = self.question.kind
        return context
