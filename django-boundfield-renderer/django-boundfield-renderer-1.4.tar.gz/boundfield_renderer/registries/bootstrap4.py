from django import forms
from ..registry import RendererRegistry
from ..utils import template_renderer

# Helper functions
def get_widget(attrs = None):
	'''Return the rendered widget with extra attrs'''
	def render_widget(boundfield):
		local_attrs = dict()
		if attrs:
			local_attrs.update(attrs)
		if boundfield.errors:
			local_attrs['class'] = ' '.join([local_attrs.get('class', ''), 'is-invalid'])
		return boundfield.as_widget(attrs = local_attrs)
	return render_widget

# Create the registry with all Django built-in form fields
renderer_registry = RendererRegistry({
	forms.BooleanField: template_renderer('bootstrap4/form-check.html', widget=get_widget({'class': 'form-check-input'})),
	forms.CharField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.ChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.TypedChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.DateField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.DateTimeField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.DecimalField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.DurationField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.EmailField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.FileField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control-file'})),
	forms.FilePathField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.FloatField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.ImageField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control-file'})),
	forms.IntegerField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.GenericIPAddressField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.MultipleChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.TypedMultipleChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.NullBooleanField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.RegexField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.SlugField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.TimeField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.URLField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.UUIDField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.ComboField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.SplitDateTimeField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.ModelChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
	forms.ModelMultipleChoiceField: template_renderer('bootstrap4/form-group.html', widget=get_widget({'class': 'form-control'})),
})
