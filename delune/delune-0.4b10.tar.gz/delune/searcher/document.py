from rs4 import unistr
import json

class Document:
	def __init__ (self, _id = None, analyzer = None):
		self._id = _id and str (_id) or None
		self.fields = {}
		self.stored = []
		self.summary = None
		self.analyzer = analyzer
	
	def add_field (self, name, value, ftype = "Text", lang = "en", option = [], format = None):
		if self._id and name == "_id":
			raise AssertionError ("_id field should be with document initialization")
			
		if type (option) is str:
			option = option.split ()
			
		if ftype == "Fnum":			
			try: 
				format = [int (each) for each in format.split (".", 1)]
				assert len (format) in (1, 2)
			except: 
				raise TypeError ("Invalid Format")
			
			if len (format) == 2:
				a, b = format
			else:
				a, b = fomat [0], 0
			
			a += (b + 1)
			ftype += ("%d.%d" % (a, b))
		
		self.fields [name] = (value, ftype, lang, option)			
	
	def set_contents (self, contents):
		self.stored = contents
		
	def add_content (self, content):		
		# any encoding even allowed python objects
		self.stored.append (content)			
		
	def set_snippet (self, text, lang = "en", option = []):
		if type (option) is str:
			option = option.split ()
		# text SHOUL BE string type, DO CEHCK
		self.summary = (text, lang, option)
			
	def as_dict (self):
		fields = {}
		if self._id:
			fields ['_id'] = str (self._id)
			
		for k, v in self.fields.items ():
			fields [k] = {'data': v [0], 'type': v [1], 'lang': v [2], 'option': v [3]}
		
		return {
			'snippet': self.summary,
			'contents': self.stored,
			'fields': fields
		}
	
	def as_json (self):
		return json.dumps (self.as_dict ())
		
