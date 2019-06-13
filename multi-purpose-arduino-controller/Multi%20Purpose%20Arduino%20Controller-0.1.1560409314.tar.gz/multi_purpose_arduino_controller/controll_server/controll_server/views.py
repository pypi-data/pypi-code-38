from django import forms
from django.forms import ModelForm
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "index.html")


def read_only_form(form: ModelForm):
    for key in form.fields.keys():
        if isinstance(form.fields[key].widget, forms.Select):
            form.fields[key].widget = forms.TextInput()
        form.fields[key].widget.attrs["readonly"] = True

    return form
