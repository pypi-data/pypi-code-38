from decimal import Decimal
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

def template_renderer(template_name, **kwargs):
	'''
	A utility fonction that return a renderer function that renders a template by passing it the context.
	Optional keywords can be specified to be added to the context before rendering the template.
	If the value of the keyword is callable, it will be called with the boundfield as parameter.
	Examples:
	template_renderer('path/to/my_template.html', color = 'red')
	This will add the item ('color': 'red') to the context before rendering the template
	
	template_renderer('path/to/my_template.html', color = lambda b: 'red' if b.value() < 0 else 'blue')
	This will add the item ('color': 'red') to the context if the value of the boundfield is negative,
	else it will add the the item ('color': 'blue') before rendering the template.
	'''
	def render_template(context):
		template = get_template(template_name)
		boundfield = context['boundfield']
		for key, value in kwargs.items():
			if callable(value):
				context[key] = value(boundfield)
			else:
				context[key] = value
		return template.render(context)
	return render_template
