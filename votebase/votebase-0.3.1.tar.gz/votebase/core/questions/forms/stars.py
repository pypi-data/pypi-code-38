from django import forms
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.forms.general import ImageForm, QuestionForm, CategoryForm
from votebase.core.questions.forms.radio import VoteRadioForm, VoterRadioForm
from votebase.core.questions.models import Question
from votebase.core.utils.widgets import RatingRadioFieldRenderer


class StarsForm(QuestionForm, CategoryForm, ImageForm):
    MIN_STARS = 3
    MAX_STARS = 10
    num_stars = forms.ChoiceField(label=_(u'Number of stars'),
        widget=forms.Select(attrs={'class': 'span3'}))

    class Meta:
        model = Question
        fields = ('title', 'is_required',
                  'image_icon', 'image', 'image_size', 'image_position',
                  'category_icon', 'category',
                  'num_stars',)
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 1,
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')
            }),
            'image_position': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(StarsForm, self).__init__(*args, **kwargs)
        choices = []
#        for i in range(self.MIN_STARS, self.MAX_STARS + 1):
        for i in [3,5,7,10]:
            choices.append((i, i))
#        choices = [(3,3), (5,5), (7,7), (10,10)]

        self.fields['title'].label = ''
        self.fields['num_stars'].choices = choices
        self.fields['num_stars'].initial = self.MAX_STARS / 2


class VoteStarsForm(VoteRadioForm):
    options = forms.ChoiceField(widget=forms.RadioSelect(renderer=RatingRadioFieldRenderer))

    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteStarsForm, self).__init__(question, number, *args, **kwargs)
        self.fields['options'].widget.attrs['class'] = 'star required'


class VoterStarsForm(VoterRadioForm):
    options = forms.ChoiceField(widget=forms.RadioSelect(renderer=RatingRadioFieldRenderer))

    def __init__(self, question, voter, number=1, *args, **kwargs):
        super(VoterStarsForm, self).__init__(question, voter, number, *args, **kwargs)
        self.fields['options'].widget.attrs['class'] = 'star required'
