"""Blob host forms
"""
from django import forms


class BLOBHostForm(forms.Form):
    """BLOB Host Upload Form
    """

    file = forms.FileField(label='')
