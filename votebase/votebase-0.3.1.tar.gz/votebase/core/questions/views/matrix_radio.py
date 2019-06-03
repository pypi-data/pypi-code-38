from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from votebase.core.questions.forms.general import OptionForm
from votebase.core.questions.forms.matrix_radio import MatrixRadioForm
from votebase.core.questions.models import Question, Option
from votebase.core.questions.views.general import OptionsQuestionCreateView, OptionsQuestionUpdateView


class MatrixRadioCreateView(OptionsQuestionCreateView):
    template_name = 'questions/matrix/form.html'
    form_class = MatrixRadioForm
    kind = Question.KIND_MATRIX_RADIO
    option_form_class = OptionForm
    add_column = False
    can_add_column = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.POST:
            ColumnOptionsFormSet = formset_factory(self.option_form_class)
            self.formset_columns = ColumnOptionsFormSet(request.POST, request.FILES, prefix='columns')
            self.add_column = 'add_column' in request.POST
        else:
            ColumnOptionsFormSet = formset_factory(self.option_form_class, extra=2)
            self.formset_columns = ColumnOptionsFormSet(prefix='columns')

        # disable empty values to extra forms
        for form in self.formset_columns.forms:
            form.empty_permitted = False

        return super(MatrixRadioCreateView, self).dispatch(request, *args,
            **kwargs)

    def get_success_url(self):
        if self.add_column:
            update_url = 'questions_update_%s' % self.kind.lower()
            return reverse(update_url, args=(self.object.pk, ))
        else:
            return super(MatrixRadioCreateView, self).get_success_url()

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_columns = self.formset_columns

        if formset_columns.is_valid():
            return super(MatrixRadioCreateView, self).post(
                request, *args, **kwargs)
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
            option.orientation = Option.ORIENTATION_ROW
            option.save()

        for f in self.formset_columns.forms:
            option = f.save(commit=False)
            option.question = self.object
            option.orientation = Option.ORIENTATION_COLUMN
            option.save()

        messages.success(self.request, _(u'Question successfully created.'))

        if self.add_option:
            Option.objects.create(
                title=_(u'New option'),
                orientation = Option.ORIENTATION_ROW,
                question=self.question
            )
            messages.success(self.request, _(u'Row option successfully created.'))

        if self.add_column:
            Option.objects.create(
                title=_(u'New option'),
                orientation = Option.ORIENTATION_COLUMN,
                question=self.question
            )
            messages.success(self.request, _(u'Column option successfully created.'))

        return super(OptionsQuestionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MatrixRadioCreateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Create radio matrix')
        context['content_title'] = _(u'Create radio matrix')
        context['formset_columns'] = self.formset_columns

        if self.can_add:
            context['submit_buttons'] = [
                    {
                    'label': 'Add row option',
                    'name': 'add_option'
                }
            ]

        if self.can_add_column:
            context['submit_buttons'].append(
                    {
                    'label': 'Add column option',
                    'name': 'add_column'
                }
            )

        return context


class MatrixRadioUpdateView(OptionsQuestionUpdateView):
    template_name = 'questions/matrix/form.html'
    form_class = MatrixRadioForm
    kind = Question.KIND_MATRIX_RADIO
    option_form_class = OptionForm
    add_column = False
    can_add_column = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if request.POST:
            #rows
            OptionsFormSet = modelformset_factory(
                Option, extra=0, form=self.option_form_class, can_delete=self.can_delete)
            self.formset = OptionsFormSet(request.POST, request.FILES,
                )
            self.add_option = 'add_option' in request.POST

            #columns
            ColumnOptionsFormSet = modelformset_factory(
                Option, extra=0, form=self.option_form_class, can_delete=self.can_delete)
            self.formset_columns = ColumnOptionsFormSet(request.POST, request.FILES,
                prefix='columns')
            self.add_column = 'add_column' in request.POST
        else:
            #rows
            OptionsFormSet = modelformset_factory(
                Option, extra=0, form=self.option_form_class, can_delete=self.can_delete)
            self.formset = OptionsFormSet(queryset=self.question.option_set.all().filter(orientation=Option.ORIENTATION_ROW))

            #columns
            ColumnOptionsFormSet = modelformset_factory(
                Option, extra=0, form=self.option_form_class, can_delete=self.can_delete)
            self.formset_columns = ColumnOptionsFormSet(queryset=self.question.option_set.all().filter(orientation=Option.ORIENTATION_COLUMN), prefix='columns')

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title,
             reverse('questions_index', args=(self.survey.pk, ))),
        ])

        # IMPORTANT! skip OptionsQuestionUpdateView dispatch!
        return super(OptionsQuestionUpdateView, self).dispatch(request, *args,
            **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset
        formset_columns = self.formset_columns

        try:
            num_options = Option.objects.rows_by_question(self.question).count()
            if self.add_option:
                num_options += 1
            marked_for_delete = self.formset.deleted_forms
            num_to_delete = len(marked_for_delete)

            if num_options - num_to_delete < 2 and num_to_delete > 0:
                form.errors['__all__'] = [
                    _(u'You must keep at least 2 row options!'),
                ]
        except AttributeError:
            pass

        try:
            num_columns = Option.objects.columns_by_question(self.question).count()
            if self.add_column:
                num_columns += 1
            marked_for_delete_columns = self.formset_columns.deleted_forms
            num_to_delete = len(marked_for_delete_columns)

            if num_columns - num_to_delete < 2 and num_to_delete > 0:
                error_message = _(u'You must keep at least 2 column options!')
                if '__all__' in form.errors:
                    form.errors['__all__'].append(error_message)
                else:
                    form.errors['__all__'] = [error_message,]
        except AttributeError:
            pass

        if form.is_valid() and formset.is_valid() and formset_columns.is_valid():
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

        try:
            marked_for_delete_columns = self.formset_columns.deleted_forms
        except AttributeError:
            marked_for_delete_columns = []

        self.need_to_delete = len(marked_for_delete) > 0 or len(marked_for_delete_columns) > 0

        for f in self.formset.forms:
            if f in marked_for_delete:
                f.instance.delete()
            else:
                # WARNING: Don't save form marked for delete!
                # It could raise ValidationError!
                f.save()

        for f in self.formset_columns.forms:
            if f in marked_for_delete_columns:
                f.instance.delete()
            else:
                # WARNING: Don't save form marked for delete!
                # It could raise ValidationError!
                f.save()

        messages.success(self.request, _(u'Question successfully updated.'))

        if self.add_option:
            Option.objects.create(
                title=_(u'New option'),
                orientation=Option.ORIENTATION_ROW,
                question=self.question
            )
            messages.success(self.request, _(u'Row option successfully created.'))

        if self.add_column:
            Option.objects.create(
                title=_(u'New option'),
                orientation=Option.ORIENTATION_COLUMN,
                question=self.question
            )
            messages.success(self.request, _(u'Column option successfully created.'))

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super(MatrixRadioUpdateView, self).get_form(form_class)
        form.fields['image'].widget.attrs['remove_url'] =\
        reverse('questions_delete_image', args=(self.question.pk, ))
        return form

    def get_success_url(self):
        if self.add_column:
            update_url = 'questions_update_%s' % self.kind.lower()
            return reverse(update_url, args=(self.object.pk, ))
        else:
            return super(MatrixRadioUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        context = super(MatrixRadioUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Update radio matrix')
        context['content_title'] = _(u'Update radio matrix')
        context['formset_columns'] = self.formset_columns

        if self.can_add:
            context['submit_buttons'] = [
                    {
                    'label': 'Add row option',
                    'name': 'add_option'
                }
            ]

        if self.can_add_column:
            context['submit_buttons'].append(
                    {
                    'label': 'Add column option',
                    'name': 'add_column'
                }
            )

        return context
