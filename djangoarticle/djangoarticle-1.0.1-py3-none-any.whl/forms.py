from django import forms
from django.forms import ModelForm
""" Import from local app. """
from .models import CategoryModelScheme
from .models import ArticleModelScheme


""" start category form here. """
class CategoryFormScheme(ModelForm):

    class Meta:
        model   = CategoryModelScheme

        fields  = ['serial', 'title', 'description', 'status']

        labels  = {
            'serial': 'Post number',
            'title': 'Category title',
            'description': 'Category description',
            'status': 'Status'
        }

        widgets = {
            'serial': forms.NumberInput(attrs={'class': 'input-number', 'type': 'number'}),
            'title': forms.TextInput(attrs={'type': 'text', 'placeholder':'Category title'}),
            'description': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder':'Article description', 'style': 'margin-bottom: 0;'})
        }
""" end category form here. """


""" start apptwo article form here. """
class ArticleFormScheme(ModelForm):

    class Meta:

        model = ArticleModelScheme

        fields = [ 'serial', 'cover_image', 'title', 'category', 'description', 'shortlines',
                   'content', 'status', 'total_views', 'verification', 'is_promote', 'is_trend' ]

        labels = { 'serial': 'Serial Number',
                   'cover_image': 'Cover image',
                   'title': 'Title',
                   'category': 'Category',
                   'description': 'Description',
                   'shortlines': 'Shortlines',
                   'content': 'Content',
                   'status': 'Status',
                   'total_views': 'Total views',
                   'verification': 'Verify',
                   'is_promote': 'Promote',
                   'is_trend': 'Trend', }

        widgets = { 'serial': forms.NumberInput(attrs={'class': 'input-number', 'type': 'number'}),
                    'cover_image': forms.FileInput(attrs={'type': 'file', 'id': 'exampleFileUpload', 'class': 'show-for-sr'}),
                    'title': forms.TextInput(attrs={'type': 'text', 'placeholder':'Article title'}),
                    'description': forms.Textarea(attrs={'type': 'text', 'rows': '3', 'placeholder':'Article description', 'style': 'margin-bottom: 0;'}),
                    'shortlines': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder':'Article shortlines', 'style': 'margin-bottom: 0;'}),
                    'content': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder':'Article content', 'style': 'margin-bottom: 0;'}),
                    'total_views': forms.NumberInput(attrs={'class': 'input-number', 'type': 'number'}),
                    'verification': forms.CheckboxInput(attrs={}),
                    'is_promote': forms.CheckboxInput(attrs={}),
                    'is_trend': forms.CheckboxInput(attrs={}),
                   }
""" end apptwo article form here. """
