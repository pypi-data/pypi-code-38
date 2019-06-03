"""Advanced blob hostforms
"""
from django import forms


class URLForm(forms.Form):
    """BLOB Host URL form
    """
    url = forms.URLField(label='')