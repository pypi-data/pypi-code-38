from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EMPTY_VALUES

from votebase.core.questions.forms.general import CategoryForm
from votebase.core.questions.forms.textfield import VoteTextfieldForm, \
    VoterTextfieldForm
from votebase.core.questions.models import Question
from votebase.core.utils.mixins import PickadayFormMixin
from votebase.core.voting.models import Answer


class DateForm(CategoryForm):
    class Meta:
        model = Question
        fields = ('title', 'is_required',
                  'category_icon', 'category',)
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input-block-level',
                'placeholder': _(u'Enter question title')
            }),
            }

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class VoteDateForm(PickadayFormMixin, VoteTextfieldForm):
#    custom = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-block-level datepicker'}), format='%d.%m.%Y)
#    custom = forms.DateField(widget=forms.DateInput(
#        format='%Y-%m-%d', attrs={
#            'class': 'datepicker',
#            'value': '',
#        }), input_formats=('%Y-%m-%d',))

    custom = forms.DateField(
        label=_(u'Date of birth'),
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.DateInput(format=settings.DATE_FORMAT, attrs={
            'class': 'datepicker',
            'value': '',
            })
    )

    class Meta:
        model = Answer
        fields = ('custom', )
        widgets = {
#            'custom': forms.SplitDateTimeWidget(),
        }

    def __init__(self, question, number=1, *args, **kwargs):
        super(VoteDateForm, self).__init__(question, number, *args, **kwargs)
        self.fix_fields(*args, **kwargs)

    def clean(self):
        date = self.cleaned_data.get('custom')

        if isinstance(self.fields['custom'].widget, forms.SplitDateTimeWidget):
            if self.fields['custom'].required:
                date_list = eval(date)
                for value in date_list:
                    if value in EMPTY_VALUES:
                        raise forms.ValidationError(_('This field is required!'))

        return super(VoteDateForm, self).clean()

class VoterDateForm(VoterTextfieldForm):
    pass
