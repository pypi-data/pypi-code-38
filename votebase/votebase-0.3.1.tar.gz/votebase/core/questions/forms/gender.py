from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.general import CategoryForm
from votebase.core.questions.forms.radio import VoterRadioForm
from votebase.core.questions.models import Question, Option
from votebase.core.utils.widgets import BootstrapRadioFieldRenderer
from votebase.core.voting.models import Answer


class GenderForm(CategoryForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required',
                  'category_icon', 'category',)
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 1,
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')
            }),
            }

    def __init__(self, *args, **kwargs):
        super(GenderForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class VoteGenderForm(forms.ModelForm):
    options = forms.ChoiceField(
        widget=forms.RadioSelect(renderer=BootstrapRadioFieldRenderer))

    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteGenderForm, self).__init__(*args, **kwargs)
        self.question = question

        if not question.is_required:
            self.fields['options'].required = False

        choices = self.question.option_set.all().values_list('pk', 'title')
        self.fields['options'].label = self.question.get_label(number)
        self.fields['options'].choices = choices

    def save(self, voter, commit=True):
        self.instance.question = self.question
        self.instance.voter = voter

        option_pk = self.cleaned_data['options']
        if len(option_pk) is not 0:
            option = Option.objects.get(pk=option_pk)
            self.instance.option = option
        return super(VoteGenderForm, self).save(commit)

    class Meta:
        model = Answer
        fields = ('options', )


class VoterGenderForm(VoterRadioForm):
    pass
