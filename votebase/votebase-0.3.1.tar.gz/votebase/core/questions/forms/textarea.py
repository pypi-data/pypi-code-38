from django import forms

from votebase.core.questions.forms.textfield import TextfieldForm, \
    VoteTextfieldForm, VoterTextfieldForm
from votebase.core.voting.models import Answer


class TextareaForm(TextfieldForm):
    pass


class VoteTextareaForm(VoteTextfieldForm):
    class Meta:
        model = Answer
        fields = ('custom',)
        widgets = {
            'custom': forms.Textarea(attrs={'class': 'input-block-level'}),
        }


class VoterTextareaForm(VoterTextfieldForm):
    class Meta:
        model = Answer
        fields = ('custom', )
        widgets = {
            'custom': forms.Textarea(attrs={'class': 'input-block-level'}),
        }
