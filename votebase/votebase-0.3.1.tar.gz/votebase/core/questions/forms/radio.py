from django import forms
from django.utils.translation import ugettext as _

from votebase.core.questions.forms.general import ImageForm, QuizForm, CategoryForm
from votebase.core.questions.models import Question, Option
from votebase.core.utils.widgets import SexyFileInput, QuizRadioFieldRenderer
from votebase.core.voting.models import Answer


class RadioForm(QuizForm, CategoryForm, ImageForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required', 'is_quiz',
                  'image_icon', 'image_position', 'image_size', 'image',
                  'category_icon', 'category',)
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 1,
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')}),
            'image_position': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(RadioForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''
        self.fields['image'].widget = SexyFileInput(attrs={'crop': False})


class VoteRadioForm(forms.ModelForm):
    options = forms.ChoiceField(widget=forms.RadioSelect())

    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteRadioForm, self).__init__(*args, **kwargs)
        self.number = number
        self.question = question

        if not question.is_required:
            self.fields['options'].required = False

        self.fields['options'].label = self.question.get_label(number)
        self.fields['options'].choices = self.question.get_image_choices()

    def save(self, voter, commit=True):
        self.instance.question = self.question
        self.instance.voter = voter

        option_pk = self.cleaned_data.get('options', 0)
        if len(option_pk) is not 0:
            option = Option.objects.get(pk=option_pk)
            self.instance.option = option

        return super(VoteRadioForm, self).save(commit)

    class Meta:
        model = Answer
        fields = ('options', )


class DesignRadioForm(VoteRadioForm):
    options = forms.ChoiceField(widget=forms.RadioSelect(renderer=QuizRadioFieldRenderer))

    def __init__(self, question, number=1, *args, **kwargs):
        super(DesignRadioForm, self).__init__(question, *args, **kwargs)
        self.number = number
        self.question = question

        if not question.is_required:
            self.fields['options'].required = False

        self.fields['options'].label = self.question.get_label(number)
        self.fields['options'].choices = self.question.get_image_choices()

        # correct options
        self.fields['options'].widget.attrs['correct_options'] = []
        if question.is_quiz:
            self.fields['options'].widget.attrs['correct_options'] =\
            Option.objects.correct(question).values_list('id', flat=True)

    class Meta:
        model = Answer
        fields = ('options', )


class VoterRadioForm(VoteRadioForm):
    options = forms.ChoiceField(widget=forms.RadioSelect(renderer=QuizRadioFieldRenderer))

    def __init__(self, question, voter, *args, **kwargs):
        self.show_quiz_correct_options = kwargs.pop('show_quiz_correct_options') if 'show_quiz_correct_options' in kwargs else False

        super(VoterRadioForm, self).__init__(question, *args, **kwargs)
        self.question = question
        self.voter = voter
        self.fields['options'].widget.attrs['disabled'] = 'disabled'

        # correct options
        self.fields['options'].widget.attrs['correct_options'] = []
        if question.is_quiz and self.show_quiz_correct_options:
            self.fields['options'].widget.attrs['correct_options'] = \
            Option.objects.correct(question).values_list('id', flat=True)

        # find answer
        answers = Answer.objects.filter(voter=voter, question=question)

        try:
            answer = answers[0]
            if answer is not None and answer.option is not None:
                self.fields['options'].initial = answer.option.pk

        except IndexError:
            pass

    @staticmethod
    def get_result(question, voter):
        correct_options = question.option_set.filter(is_correct=True).values_list('id', flat=True)

        try:
            answer = Answer.objects.filter(voter=voter, question=question).values_list('option_id', flat=True)[0]
        except IndexError:
            return not len(correct_options)

        return 1 if answer in correct_options else 0
