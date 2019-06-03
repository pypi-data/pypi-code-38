from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.radio import RadioForm
from votebase.core.questions.models import Question, Option
from votebase.core.utils.fields import MatrixField
from votebase.core.voting.models import Answer


class MatrixRadioForm(RadioForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required', 'is_unique_answers', 'is_empty_row_enabled',
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

    def clean_is_empty_row_enabled(self):
        is_required = self.cleaned_data.get('is_required')
        is_unique_answers = self.cleaned_data.get('is_unique_answers')
        is_empty_row_enabled = self.cleaned_data.get('is_empty_row_enabled')

        if not is_required and not is_empty_row_enabled:
            raise ValidationError(_(u"You can't disable empty rows if questions is not required."))
        if is_unique_answers and is_empty_row_enabled:
            raise ValidationError(_(u"You can't enable empty rows if questions require unique answers."))
        return is_empty_row_enabled


class VoteMatrixRadioForm(forms.Form):
    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteMatrixRadioForm, self).__init__(*args, **kwargs)
        self.question = question
        self.rows = question.option_set.orientation_row().prepare_as_list()
        self.columns = question.option_set.orientation_column().prepare_as_list()

        self.fields['matrix'] = MatrixField(
            label=question.title, rows=self.rows, columns=self.columns,
            required=question.is_required,
            unique_answers=question.is_unique_answers,
            empty_row_enabled=question.is_empty_row_enabled)

        self.fields['matrix'].label = self.question.get_label(number)

    def save(self, voter, commit=True):
        options = self.cleaned_data.get('matrix', '').split('-')

        for index, option_pk in enumerate(options):
            if option_pk is None or option_pk == '' or len(option_pk) is 0:
                continue

            option_column = Option.objects.get(pk=option_pk)
            option = Option.objects.get(pk=self.rows[index][0])
            Answer.objects.create(
                question=self.question,
                voter=voter,
                option=option,
                option_column=option_column,
            )


class VoterMatrixRadioForm(VoteMatrixRadioForm):
    def __init__(self, question, voter, *args, **kwargs):
        super(VoterMatrixRadioForm, self).__init__(question, initial={
            'matrix': Answer.objects.get_vote_for_matrix(voter, question)
        }, *args, **kwargs)
        self.fields['matrix'].widget.attrs['disabled'] = 'disabled'
