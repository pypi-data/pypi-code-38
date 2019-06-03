from rest_framework.fields import SerializerMethodField


class ConfigSerializerMethodField(SerializerMethodField):
	"""
	class Book(models.Model):
		name = 'test'
		desc = 'desc'

	class ExampleSerializer(self):
		book_name = ConfigSerializerMethodField(relation_field='book', get_field='name') (return "book_name": "test")
		full_data = ConfigSerializerMethodField(relation_field='book', get_field=['name', 'desc']) (return "book_name": "test desc")
	"""
	def __init__(self,method_name=None, relation_field=None, get_field=None, split_value=None, split_index=None, default_value='none',allow_empty=True, **kwargs):
		self.method_name = method_name
		self.relation_field = relation_field
		self.get_field = get_field
		self.default_value = default_value
		self.split_value = split_value
		self.split_index = split_index
		self.allow_empty = allow_empty
		kwargs['source'] = '*'
		kwargs['read_only'] = True
		super(SerializerMethodField, self).__init__(**kwargs)


	def ensure_obj(self, obj):
		if isinstance(obj, dict):
			return self._create_dict_value(obj)

		if self.relation_field:
			try:
				obj = getattr(obj, self.relation_field)
			except AttributeError:
				return self.default_value
		if not obj:
			return self.default_value
		
		return self._create_model_value(obj)
		

	def _create_dict_value(self, obj):
		attr = ""
		if isinstance(self.get_field, str):
			attr = obj.get(self.get_field)
		elif isinstance(self.get_field, list):
			values = [obj.get(field) for field in self.get_field]
			attr = " ".join(str(v) for v in values if v)
		if not attr and not self.allow_empty:
			return self.default_value

		if self.split_value:
			return self.get_split(attr)
		
		return attr


	def _create_model_value(self, obj):
		attr = ""
		if isinstance(self.get_field, str):
			attr = getattr(obj, self.get_field)
		elif isinstance(self.get_field, list):
			values = [getattr(obj, field) for field in self.get_field]
			attr = " ".join(str(v) for v in values if v)
		if not attr and not self.allow_empty:
			return self.default_value

		if self.split_value:
			return self.get_split(attr)
		
		return attr


	def get_split(self, value):
		splited = value.split(self.split_value)
		try:
			return splited[self.split_index]
		except (TypeError, IndexError, ValueError):
			return self.default_value

	def to_representation(self, value):
		return self.ensure_obj(value)
