from ordereddict import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import UpdateView

from votebase.core.questions.forms.general import QuizOptionImageForm
from votebase.core.questions.models import Question, Option
from votebase.core.surveys.models import Survey


class IndexView(ListView):
    model = Question
    template_name = 'questions/index.html'

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))
        if self.survey.user != request.user:
            return HttpResponseForbidden()
        request.breadcrumbs([(_(u'Surveys'), reverse('surveys_index')), ])
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(IndexView, self).get_queryset()
        queryset = queryset.filter(survey=self.survey).prefetch_related('option_set')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        return context

    def post(self, request, pk):
        questions_list = request.POST.getlist('order[]')

        for key, value in enumerate(questions_list):
            question = Question.objects.get(pk=value)
            question.weight = key
            question.save()

        return HttpResponse()


class PreviewView(TemplateResponseMixin, View):
    template_name = 'questions/preview.html'

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk', ))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if self.survey.title == _('Your new survey'):
            messages.error(
                request, _(u'Please, change the default survey title by clicking on it.'))
            return redirect(reverse(
                'questions_index', args=(self.survey.pk, )))
            
        self.questions = self.survey.question_set.all().prefetch_related('option_set')

        request.breadcrumbs([(_(u'Surveys'), reverse('surveys_index')), ])

        return super(PreviewView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return self.render_to_response({
            'survey': self.survey,
            'questions': self.questions,
            'question_forms': [question.get_voting_form(number=index + 1) for index, question in enumerate(self.questions)],
        })


class QuestionDeleteView(View):
    success_url = 'questions_index'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs.get('pk'))
        survey = get_object_or_404(Survey, pk=question.survey.pk)

        if survey.user != request.user:
            return HttpResponseForbidden()

        question.delete()

        messages.success(request, _(u'Question successfully deleted.'))

        return redirect(reverse(self.success_url, args=(survey.pk,)))


class OptionsQuestionCreateView(CreateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = None
    option_form_class = QuizOptionImageForm
    kind = None
    add_option = False
    can_add = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if request.POST:
            OptionsFormSet = formset_factory(self.option_form_class)
            self.formset = OptionsFormSet(request.POST, request.FILES)
            self.add_option = 'add_option' in request.POST
        else:
            OptionsFormSet = formset_factory(self.option_form_class, extra=2)
            self.formset = OptionsFormSet()

        # disable empty values to extra forms
        for form in self.formset.forms:
            form.empty_permitted = False

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(OptionsQuestionCreateView, self).dispatch(request, *args,
            **kwargs)

    def get_success_url(self):
        if self.add_option:
            update_url = 'questions_update_%s' % self.kind.lower()
            return reverse(update_url, args=(self.object.pk, ))
        else:
            return reverse(self.success_url, args=(self.survey.pk, ))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.question = self.object
        self.object.survey = self.survey
        self.object.kind = self.kind
        self.object.save()

        for f in self.formset.forms:
            option = f.save(commit=False)
            option.question = self.object
            option.save()

        messages.success(self.request, _(u'Question successfully created.'))

        if self.add_option:
            Option.objects.create(
                title=_(u'New option'),
                question=self.question
            )
            messages.success(self.request, _(u'Option successfully created.'))

        return super(OptionsQuestionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(OptionsQuestionCreateView, self).get_context_data(**kwargs)
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['formset'] = self.formset
        context['kind'] = self.kind
        action_url = 'questions_create_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.survey.pk,))

        if self.can_add:
            context['submit_buttons'] = [
                    {
                    'label': _(u'Add option'),
                    'name': 'add_option'
                },
            ]
        return context


class OptionsQuestionUpdateView(UpdateView):
    template_name = 'questions/helpers/form.html'
    success_url = 'questions_index'
    model = Question
    form_class = None
    option_form_class = QuizOptionImageForm
    kind = None
    add_option = False
    can_delete = True
    can_add = True
    can_order = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if request.POST:
            OptionsFormSet = inlineformset_factory(
                Question, Option, extra=0, form=self.option_form_class,
                can_delete=self.can_delete, can_order=self.can_order)
            self.formset = OptionsFormSet(request.POST, request.FILES,
                instance=self.question)
            self.add_option = 'add_option' in request.POST

            if len(self.formset.ordered_forms) == len(self.formset.forms):
                self.forms = self.formset.ordered_forms
            else:
                self.forms = self.formset.forms
        else:
            OptionsFormSet = inlineformset_factory(
                Question, Option, extra=0, form=self.option_form_class,
                can_delete=self.can_delete, can_order=self.can_order)
            self.formset = OptionsFormSet(instance=self.question)
            self.forms = self.formset.forms

        for key, value in enumerate(self.forms):
            fields = value.fields

            new_fields = [
                ('id', fields['id']),
                ('title', fields['title']),
            ]

            if 'image_icon' in fields:
                value.fields['image'].widget.attrs['remove_url'] =\
                reverse('questions_delete_image_option', args=(value.instance.pk, ))

            if 'DELETE' in fields:
                delete = fields['DELETE']

            if 'ORDER' in fields:
                order = fields['ORDER']
                order.label = ''
                order.widget.attrs = {
                    'append': _(u'Order'),
                    'append_class': 'move',
                    'class': 'order',
                    }
                new_fields.append(('ORDER', order))

            if self.can_delete:
                new_fields.append(('DELETE', delete),)

            if 'image_icon' in fields:
                new_fields.append(('image_icon', fields['image_icon'] if 'image_icon' in fields else None))
                new_fields.append(('image_position', fields['image_position'] if 'image_position' in fields else None))
                new_fields.append(('image', fields['image'] if 'image' in fields else None))

            try:
                new_fields.append(('is_correct', fields['is_correct']))
            except KeyError:
                pass

            self.formset.forms[key].fields = OrderedDict(new_fields)

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
        ])

        return super(OptionsQuestionUpdateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset

        try:
            num_options = Option.objects.by_question(self.question).count()
            if self.add_option:
                num_options += 1
            marked_for_delete = self.formset.deleted_forms
            num_to_delete = len(marked_for_delete)

            if num_options - num_to_delete < 2 and num_to_delete > 0:
                form.errors['__all__'] = [
                    _(u'You must keep at least 2 options!')]
        except AttributeError:
            pass

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()

        # delete forms marked for deletion
        try:
            marked_for_delete = self.formset.deleted_forms
        except AttributeError:
            marked_for_delete = []

        self.need_to_delete = len(marked_for_delete) > 0

        for f in marked_for_delete:
            f.instance.delete()

        for key, f in enumerate(self.formset.ordered_forms):
            if f not in marked_for_delete:
                f.instance.weight = key
                f.save()

        messages.success(self.request, _(u'Question successfully updated.'))

        if self.add_option:
            Option.objects.create(
                title=_(u'New option'),
                question=self.question
            )
            messages.success(self.request, _(u'Option successfully created.'))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.add_option or self.need_to_delete:
            update_url = 'questions_update_%s' % self.kind.lower()
            return reverse(update_url, args=(self.object.pk, ))
        else:
            return reverse(self.success_url, args=(self.survey.pk, ))

    def get_context_data(self, **kwargs):
        context = super(OptionsQuestionUpdateView, self).get_context_data(**kwargs)
        context['submit_label'] = _(u'Done')
        context['survey'] = self.survey
        context['formset'] = self.formset
        context['kind'] = self.kind
        action_url = 'questions_update_%s' % self.kind.lower()
        context['action_url'] = reverse(action_url, args=(self.question.pk,))

        if self.can_add:
            context['submit_buttons'] = [
                    {
                    'label': _(u'Add option'),
                    'name': 'add_option'
                },
            ]
        return context


class QuestionDeleteImageView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        if self.question.survey.user != request.user:
            return HttpResponseForbidden()

        self.question.delete_image()
        self.question.image = None
        self.question.save()
        messages.success(request, _(u'Image successfully deleted.'))
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse(
            'questions_index', args=(self.question.survey.pk, )))

class OptionDeleteImageView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.option = get_object_or_404(Option, pk=kwargs.get('pk'))
        self.question = self.option.question

        if self.question.survey.user != request.user:
            return HttpResponseForbidden()

        self.option.delete_image()
        self.option.image = None
        self.option.save()
        messages.success(request, _(u'Image successfully deleted.'))
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse(
            'questions_index', args=(self.question.survey.pk, )))
