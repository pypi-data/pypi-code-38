from django import forms
from django.utils.translation import ugettext_lazy as _
from votebase.core.questions.forms.checkbox import CheckboxForm
from votebase.core.questions.models import Question, Option
from votebase.core.utils.fields import MatrixField
from votebase.core.voting.models import Answer


class TrueFalseForm(CheckboxForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required', 'is_quiz',
                  'true_label', 'false_label',
                  'image_icon', 'image', 'image_size', 'image_position',
                  'category_icon', 'category',)
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 1,
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')
            }),
            'image_position': forms.RadioSelect(),
        }


class VoteTrueFalseForm(forms.Form):
    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteTrueFalseForm, self).__init__(*args, **kwargs)
        self.number = number
        self.question = question
        self.rows = question.option_set.orientation_row().prepare_as_list()

        self.columns = [
            (True, self.question.true_label),
            (False, self.question.false_label),
        ]

        self.fields['matrix'] = MatrixField(
            label=question.title, rows=self.rows, columns=self.columns,
            required=question.is_required,
            unique_answers=question.is_unique_answers,
            empty_row_enabled=False)

        self.fields['matrix'].label = self.question.get_label(number)

    def save(self, voter, commit=True):
        options = self.cleaned_data.get('matrix', '').split('-')

        for index, option_value in enumerate(options):
            if option_value is None or option_value == '' or len(option_value) is 0 or option_value == 'False':
                continue

            option = Option.objects.get(pk=self.rows[index][0])
            Answer.objects.create(
                question=self.question,
                voter=voter,
                option=option,
            )


class VoterTrueFalseForm(VoteTrueFalseForm):
    def __init__(self, question, voter, *args, **kwargs):
        self.show_quiz_correct_options = kwargs.pop('show_quiz_correct_options') if 'show_quiz_correct_options' in kwargs else False

        super(VoterTrueFalseForm, self).__init__(question, initial={
            'matrix': Answer.objects.get_vote_for_true_false(voter, question)
        }, *args, **kwargs)

        self.voter = voter
        self.fields['matrix'].widget.attrs['disabled'] = 'disabled'

        # correct options
        self.fields['matrix'].widget.attrs['correct_options'] = []
        if question.is_quiz and self.show_quiz_correct_options:
            self.fields['matrix'].widget.attrs['correct_options'] = Option.objects.correct(question).values_list('id', flat=True)

        answers = Answer.objects\
            .filter(voter=voter, question=question)\
            .values_list('option__pk', flat=True)

        if answers is not None:
            self.fields['matrix'].initial = answers

    @staticmethod
    def get_result(question, voter):
        answers = Answer.objects.filter(voter=voter, question=question)

        # list of TRUE options
        true_options = question.option_set.filter(is_correct=True).values_list('id', flat=True)

        # list of FALSE options
        false_options = question.option_set.filter(is_correct=False).values_list('id', flat=True)

        # list od selected "Pravda" which are TRUE (correct answers)
        selected_true = answers.filter(option_id__in=true_options).values_list('option_id', flat=True)

        # list od selected "Pravda" which are FALSE (incorrect answers)
        selected_false = answers.filter(option_id__in=false_options).values_list('option_id', flat=True)

        # selected options "Pravda" which are TRUE and all FALSE options selected as "Nepravda"
        correct_answers = len(selected_true) + len(set(false_options) - set(selected_false))

        # 4/4 = 1, 3/4 = 0.75, 2/4 = 0.5, 1/4 = 0.25, 0/4 = 0
        result = float(correct_answers) / question.option_set.count()

        return round(result, 2)


class DesignTrueFalseForm(VoteTrueFalseForm):
    def __init__(self, question, number=1, *args, **kwargs):
        super(DesignTrueFalseForm, self).__init__(question, *args, **kwargs)
        self.number = number
        self.question = question

        #if not question.is_required:
        #    self.fields['matrix'].required = False

        self.fields['matrix'].label = self.question.get_label(number)
        #self.fields['matrix'].choices = self.question.get_image_choices()

        # correct options
        self.fields['matrix'].widget.attrs['correct_options'] = []
        if question.is_quiz:
            self.fields['matrix'].widget.attrs['correct_options'] =\
            Option.objects.correct(question).values_list('id', flat=True)

    class Meta:
        model = Answer
        fields = ('options', )
