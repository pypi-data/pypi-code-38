from taggit_labels.widgets import LabelWidget
from django.forms.models import ModelForm
from taggit.forms import TagField
from .models import Article


class ArticleForm(ModelForm):
    tags = TagField(required=False, widget=LabelWidget)

    class Meta:
        model = Article
        exclude = ['updated']
