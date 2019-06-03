from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.general import CategoryForm
from votebase.core.questions.forms.textfield import VoteTextfieldForm, \
    VoterTextfieldForm
from votebase.core.questions.models import Question
from votebase.core.voting.models import Answer


class PhoneForm(CategoryForm):
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
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class VotePhoneForm(VoteTextfieldForm):
    class Meta:
        model = Answer
        fields = ('custom', )
        widgets = {
            'custom': forms.TextInput(),
        }


class VoterPhoneForm(VoterTextfieldForm):
    pass
