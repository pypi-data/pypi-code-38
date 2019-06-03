from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.models import Option
from votebase.core.questions.forms.radio import RadioForm, VoteRadioForm, \
    VoterRadioForm


class SelectSingleForm(RadioForm):
    def __init__(self, *args, **kwargs):
        super(SelectSingleForm, self).__init__(*args, **kwargs)
        #self.fields.pop('is_quiz')


class VoteSelectSingleForm(VoteRadioForm):
    options = forms.ChoiceField(
        widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(VoteSelectSingleForm, self).__init__(*args, **kwargs)
        self.fields['options'].choices = [('', _('Select an option')), ] + self.fields['options'].choices


class DesignSelectSingleForm(VoteSelectSingleForm):
    def __init__(self, *args, **kwargs):
        super(DesignSelectSingleForm, self).__init__(*args, **kwargs)

        # correct options
        if self.question.is_quiz:
            correct_option_titles = Option.objects.correct(self.question).values_list('title', flat=True)
            self.fields['options'].widget.attrs['append'] = u'{}: {}'.format(
                _('Correct'), unicode(u', '.join(correct_option_titles))
            )


class VoterSelectSingleForm(VoterRadioForm):
    options = forms.ChoiceField(
        widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(VoterSelectSingleForm, self).__init__(*args, **kwargs)
        self.fields['options'].choices = [('', _('Select an option')), ] + self.fields['options'].choices
