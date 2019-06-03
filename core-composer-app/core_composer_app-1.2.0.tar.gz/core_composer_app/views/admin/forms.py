"""Composer Admin Forms
"""
from django import forms
from mongodbforms import DocumentForm

from core_composer_app.components.bucket import api as bucket_api
from core_composer_app.components.bucket.models import Bucket


class BucketForm(forms.Form):
    """
    Form to add a bucket.
    """
    label = forms.CharField(label='Enter Bucket label', max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))


class BucketDataModelChoiceField(forms.ModelMultipleChoiceField):
    """
    Choice Field to select an existing form.
    """
    def label_from_instance(self, obj):
        return obj.label


class UploadTypeForm(forms.Form):
    """
    Form to upload a new Type.
    """
    name = forms.CharField(label='Enter Type name', max_length=100, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    xsd_file = forms.FileField(label='Select a file', required=True,
                               widget=forms.FileInput(attrs={'accept':'.xsd', 'class': 'form-control'}))
    buckets = BucketDataModelChoiceField(label='Select buckets', queryset=bucket_api.get_all(), required=False,
                                         widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class EditTypeBucketsForm(forms.Form):
    """
    Form to edit buckets of a Type.
    """
    buckets = BucketDataModelChoiceField(label='Select new buckets', queryset=bucket_api.get_all(), required=False,
                                         widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class EditBucketForm(DocumentForm):
    label = forms.CharField(label='Label',
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'Enter the new label'}))

    class Meta:
        document = Bucket
        fields = ['label']
