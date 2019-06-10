from django import forms
from django.forms import ModelForm
""" Import from local app. """
from .models import CategoryModel
from .models import ArticleModel


""" start category form here. """
# start CategoryForm here.
class CategoryForm(ModelForm):

    class Meta:
        model   = CategoryModel

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
            'description': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder':'Category description', 'style': 'margin-bottom: 0;'})
        }
# CategoryForm end here.        
""" end category form here. """


""" start article form here. """
# article form
class ArticleForm(ModelForm):

    class Meta:

        model = ArticleModel

        fields = [ 'serial', 'cover_image', 'title', 'category', 'description',
                   'shortlines', 'content', 'status', 'total_views', 'verification',
                   'is_promote', 'is_trend' ]

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
                    'shortlines': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder':'Shortlines', 'style': 'margin-bottom: 0;'}),
                    'content': forms.Textarea(attrs={'type': 'text', 'rows': '14', 'placeholder': 'Content', 'style': 'margin-bottom: 0;'}),
                    'total_views': forms.NumberInput(attrs={'class': 'input-number', 'type': 'number'}),
                    'verification': forms.CheckboxInput(attrs={}),
                    'is_promote': forms.CheckboxInput(attrs={}),
                    'is_trend': forms.CheckboxInput(attrs={}),
                   }
# end article form here.                   
""" end article form here. """
