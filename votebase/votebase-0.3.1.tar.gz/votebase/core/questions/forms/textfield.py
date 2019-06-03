from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.general import ImageForm, CategoryForm
from votebase.core.questions.models import Question
from votebase.core.voting.models import Answer


class TextfieldForm(CategoryForm, ImageForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required',
                  'image_icon', 'image', 'image_size', 'image_position',
                  'category_icon', 'category',)
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 1,
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')
            }),
            'image_position': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(TextfieldForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class VoteTextfieldForm(forms.ModelForm):
    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteTextfieldForm, self).__init__(*args, **kwargs)
        self.question = question
        self.fields['custom'].label = self.question.get_label(number)
        self.fields['custom'].required = question.is_required

    def save(self, voter, commit=True):
        self.instance.question = self.question
        self.instance.voter = voter
        return super(VoteTextfieldForm, self).save(commit)

    class Meta:
        model = Answer
        fields = ('custom', )
        widgets = {
            'custom': forms.TextInput(attrs={'class': 'input-block-level'}),
        }


class VoterTextfieldForm(VoteTextfieldForm):
    def __init__(self, question, voter, *args, **kwargs):
        super(VoterTextfieldForm, self).__init__(question, *args, **kwargs)

        self.fields['custom'].widget.attrs['disabled'] = 'disabled'

        # find answer
        answers = Answer.objects.filter(voter=voter, question=question)

        try:
            answer = answers[0]
            if answer is not None and answer.custom is not None:
                self.fields['custom'].initial = answer.custom

        except IndexError:
            pass
