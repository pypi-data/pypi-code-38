from django import forms
from django.template.loader import get_template
from ..registry import RendererRegistry

# Use the field.html template render method as the renderer function
renderer = get_template('default/field.html').render

# Create the registry with all Django built-in form fields
renderer_registry = RendererRegistry({
	forms.BooleanField: renderer,
	forms.CharField: renderer,
	forms.ChoiceField: renderer,
	forms.TypedChoiceField: renderer,
	forms.DateField: renderer,
	forms.DateTimeField: renderer,
	forms.DecimalField: renderer,
	forms.DurationField: renderer,
	forms.EmailField: renderer,
	forms.FileField: renderer,
	forms.FilePathField: renderer,
	forms.FloatField: renderer,
	forms.ImageField: renderer,
	forms.IntegerField: renderer,
	forms.GenericIPAddressField: renderer,
	forms.MultipleChoiceField: renderer,
	forms.TypedMultipleChoiceField: renderer,
	forms.NullBooleanField: renderer,
	forms.RegexField: renderer,
	forms.SlugField: renderer,
	forms.TimeField: renderer,
	forms.URLField: renderer,
	forms.UUIDField: renderer,
	forms.ComboField: renderer,
	forms.SplitDateTimeField: renderer,
	forms.ModelChoiceField: renderer,
	forms.ModelMultipleChoiceField: renderer,
})

print('evaluated default')
