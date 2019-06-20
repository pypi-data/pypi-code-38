import inspect
from collections import UserDict

class RendererRegistry(UserDict):
	'''
	Registry for the form field renderers.
	
	A renderer is a function that takes a context dict and returns the html
	representation of the form field, for example the render method of a
	Template instance.
	
	'''
	
	def __getitem__(self, key):
		'''Return the best renderer function for the field'''
		
		# Look up the chain of inheritance for a registered renderer
		for form_class in inspect.getmro(key):
			try:
				return super().__getitem__(form_class)
			except KeyError:
				pass
		
		# If no renderer was found raise an Exception
		raise ValueError('No renderer found for field %s' % key)
	
	def register(self, renderer):
		'''
		Form Field class decorator to register a renderer into the registry.
		
		Example:
		from django.template.loader import get_template
		from my_registry import renderer_registry
		
		renderer_registry.register(get_template('/path/to/my_field.html').render)
		class MyField(forms.Field):
			pass
		'''
		
		def registerer(form_field_class):
			self[form_field_class] = renderer
			return form_field_class
		
		return registerer
