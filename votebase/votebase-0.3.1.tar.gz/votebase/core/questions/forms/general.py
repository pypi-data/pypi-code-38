from django import forms
from django.utils.translation import ugettext as _

from votebase.core.questions.models import Question, Option
from votebase.core.utils.widgets import SexyFileInput

###########
# OPTIONS #
###########


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('title', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'span7'}),
        }

    def __init__(self, *args, **kwargs):
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class OptionImageForm(forms.ModelForm):
    image = forms.ImageField(
        required=False, label=_(u'Image'),
        widget=SexyFileInput(attrs={'crop': False}))

    class Meta:
        model = Option
        fields = ('title', 'image', 'image_position', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'span6'}),
            'image_position': forms.Select(attrs={'class': 'span3'}),
        }


class QuizOptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('title', 'is_correct', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'span6'}),
        }

    def __init__(self, *args, **kwargs):
        super(QuizOptionForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''


class QuizOptionImageForm(forms.ModelForm):
    image_icon = forms.CharField(
        label='', required=False, widget=forms.TextInput(
            attrs={'append': _(u'image')}))
    image = forms.ImageField(
        required=False, label=_(u'Image'),
        widget=SexyFileInput(attrs={'crop': False}))

    class Meta:
        model = Option
        fields = ('is_correct', 'title', 'image_icon', 'image_position', 'image',)
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': _(u'Enter option title')}),            
            'image_position': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(QuizOptionImageForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ''        

#############
# QUESTIONS #
#############


class QuestionForm(forms.ModelForm):
    class Meta:
        fields = ('title', 'is_required', )
        model = Question


class QuizForm(forms.ModelForm):
    class Meta:
        fields = ('is_quiz', )
        model = Question


class CategoryForm(forms.ModelForm):
    category_icon = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'append': _(u'category')}))

    class Meta:
        fields = ('category_icon', 'category')
        model = Question


class ImageForm(forms.ModelForm):
    image_icon = forms.CharField(
        label='', required=False, widget=forms.TextInput(
            attrs={'append': _(u'image')}))
    image = forms.ImageField(
        required=False, label=_(u'Image attachment'),
        widget=SexyFileInput(attrs={'crop': False}))

    class Meta:
        fields = ('image_icon', 'image', 'image_position', 'image_size')
        model = Question
        widgets = {
            'image_position': forms.RadioSelect,
        }
