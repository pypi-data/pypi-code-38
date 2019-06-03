from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView

from votebase.core.questions.forms.stars import StarsForm
from votebase.core.questions.models import Question, Option
from votebase.core.surveys.models import Survey


class StarsCreateView(CreateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = StarsForm
    kind = Question.KIND_STARS

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

        return super(StarsCreateView, self).dispatch(request, *args,
            **kwargs)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.survey = self.survey
        self.object.kind = self.kind
        self.object.save()

        for i in range(1, int(form.data['num_stars'])+1):
            Option.objects.create(
                title=i,
                question=self.object,
                weight=i,
            )

        messages.success(self.request, _(u'Question successfully created.'))

        return super(StarsCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StarsCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create rating stars')
        context['content_title'] = _(u'Create rating stars')
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['kind'] = self.kind
        action_url = 'questions_create_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.survey.pk,))
        return context

class StarsUpdateView(UpdateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = StarsForm
    kind = Question.KIND_STARS

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

        return super(StarsUpdateView, self).dispatch(request, *args,
            **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=True)

        num_options = self.object.option_set.all().count()
        num_stars = int(form.data['num_stars'])

        # need more stars: create additional
        if num_options < num_stars:
            for i in range(num_options+1, num_stars+1):
                Option.objects.create(
                    title=i,
                    question=self.object,
                    weight=i
                )

        # need less stars: delete stars with big numbers
        elif num_options > num_stars:
            num_to_delete = num_options - num_stars
            objects_to_delete = Option.objects.by_question(self.object).order_by('-created')[:num_to_delete]
            Option.objects.filter(pk__in=objects_to_delete).delete()

        messages.success(self.request, _(u'Question successfully updated.'))

        return super(StarsUpdateView, self).form_valid(form)

    def get_form(self, form_class=None):
        form = super(StarsUpdateView, self).get_form(form_class)
        form.fields['image'].widget.attrs['remove_url'] =\
        reverse('questions_delete_image', args=(self.question.pk, ))
        return form

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, ))


    def get_context_data(self, **kwargs):
        context = super(StarsUpdateView, self).get_context_data(**kwargs)
        context['form'].fields['num_stars'].initial = self.question.option_set.all().count()
        context['form'].fields['num_stars'].help_text = _(u'Be careful! Changing count of stars to lower value will delete existing corresponding votes!')

        context['title'] = _(u'Update rating stars')
        context['content_title'] = _(u'Update rating stars')
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['kind'] = self.kind
        action_url = 'questions_update_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.question.pk,))
        return context
