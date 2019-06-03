from form_utils.forms import BetterModelForm

from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _

from votebase.core.surveys.models import Survey, Round, BrandingImage
from votebase.core.utils.widgets import SexyFileInput


class BrandingImageForm(forms.ModelForm):
    class Meta:
        model = BrandingImage
        fields = ('image', )
        widgets = {
            'image': SexyFileInput(),
        }


class BrandingForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ('css', )
        widgets = {
            'css': forms.Textarea(attrs={'class': 'editor'})
        }


class SurveySettingsForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ('preface', 'postface')
        widgets = {
            'preface': forms.Textarea(attrs={'class': 'redactor', 'rows': '5'}),
            'postface': forms.Textarea(attrs={'class': 'redactor', 'rows': '5'}),
        }


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ('title', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-block-level'}),
        }


class SegmentForm(BetterModelForm):
    survey = None
    email_treshold = forms.ChoiceField(label=_(u'Email treshold'),
        help_text=_(u'Determine when do you want to receive email about new voters.'),
        widget=forms.Select(attrs={'class': 'span3'}))

    class Meta:
        model = Round
        fieldsets = [
            (_(u'Basic information'), {
                'fields': ['title', 'email_treshold']
            }),
            (_(u'Time range'), {
                'fields': ['date_from', 'date_to']
            }),
            (_(u'Voting settings'), {
                'fields': ['is_active', 'is_repeatable', 'is_quiz_result_visible',
                           'is_quiz_correct_options_visible', 'count_questions']  # 'duration'
            }),
            (_(u'Security settings'), {
                'fields': ['permission_level', 'statistics_policy', 'password', ]
            }),
            (_(u'Advanced settings'), {
                'fields': ['slug', 'finish_url', 'finish_url_title']
            })
        ]

        widgets = {
            # 'date_from': forms.SplitDateTimeWidget(),
            # 'date_to': forms.SplitDateTimeWidget(),
            'permission_level': forms.Select(attrs={'class': 'span3'}),
        }

    def __init__(self, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = ''
        self.fields['email_treshold'].choices = [
            (1, _(u'Immediately')),
            (10, _(u'After 10 voters')),
            (100, _(u'After 100 voters')),
            (1000, _(u'After 1000 voters'))
        ]

    def clean_count_questions(self):
        count_questions = self.cleaned_data.get('count_questions')
        if count_questions in EMPTY_VALUES:
            return None

        survey = self.survey if self.survey else self.instance.survey
        survey_questions_count = survey.question_set.count()

        if count_questions > survey_questions_count:
            raise forms.ValidationError(
                _(u'Number has to be smaller or equal than count of '
                  u'survey questions (%d)!') % survey_questions_count)

        if not count_questions:
            raise forms.ValidationError(_(u'Number has to be bigger than 0!'))

        return count_questions

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug in EMPTY_VALUES:
            return ''
        return slug

    def clean(self):
        data = self.cleaned_data
        finish_url = data.get('finish_url')
        finish_url_title = data.get('finish_url_title')

        if finish_url in EMPTY_VALUES and finish_url_title not in EMPTY_VALUES\
        or finish_url_title in EMPTY_VALUES and finish_url not in EMPTY_VALUES:
            raise forms.ValidationError(_(u'Fill both finish URL and its title'
                                          u' or keep them blank.'))

        return super(SegmentForm, self).clean()