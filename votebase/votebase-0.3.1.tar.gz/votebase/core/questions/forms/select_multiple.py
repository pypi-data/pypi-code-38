from django import forms

from votebase.core.questions.forms.checkbox import CheckboxForm, \
    VoteCheckboxForm, VoterCheckboxForm


class SelectMultipleForm(CheckboxForm):
    def __init__(self, *args, **kwargs):
        super(SelectMultipleForm, self).__init__(*args, **kwargs)
        self.fields.pop('is_quiz')


class VoteSelectMultipleForm(VoteCheckboxForm):
    options = forms.MultipleChoiceField(
        widget=forms.SelectMultiple())


class VoterSelectMultipleForm(VoterCheckboxForm):
    options = forms.MultipleChoiceField(
        widget=forms.SelectMultiple())
