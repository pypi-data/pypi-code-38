from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.general import ImageForm, QuestionForm, CategoryForm
from votebase.core.questions.forms.radio import VoteRadioForm, VoterRadioForm
from votebase.core.questions.models import Question


class ThumbsForm(QuestionForm, CategoryForm, ImageForm):
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
        super(ThumbsForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class VoteThumbsForm(VoteRadioForm):
    pass


class VoterThumbsForm(VoterRadioForm):
    pass
