from django import forms

from votebase.core.voting.models import Voter


class VoterFlagForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ('flag', )
