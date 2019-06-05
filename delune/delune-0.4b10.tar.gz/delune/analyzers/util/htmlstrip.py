from delune import _delune

class HtmlStripHandler:
	#MULTILINE_TAGS = ("script", "style", "object")
	NEED_SPACE = ("p", "br", "td", "table", "div")
	def get_parsed (self):
		return " ".join (self.buffer)
	
	#def handle_sdata (self, data):
		#print (repr (data))
			
	def reset (self):
		self.in_multiline = False
		self.last_commit = 0
		self.buffer = []
	
	def finish_starttag (self, tag, attr):
		tag = tag.lower ()
		#if tag in self.MULTILINE_TAGS:
			#self.in_multiline = True	
		if tag in self.NEED_SPACE:
			self.handle_data (" ")
		
	#def finish_endtag (self, tag):
		#print (tag)
		#if tag in self.MULTILINE_TAGS:
		#	if not self.in_multiline:
		#		self.buffer = self.buffer [:self.last_commit]
		#	else:		
		#		self.in_multiline = False
		#	self.last_commit = len (self.buffer)
		
	def handle_data (self, data):
		#print ("+", repr (data))
		#if self.in_multiline: 
		#	return		
		data = data.strip ()
		self.buffer.append (data)



class Parser:
	def __init__ (self, handler):
		self.handler = handler
		
	def parse (self, data):			
		self.handler.reset ()
		p = _delune.SGMLParser ()
		p.register (self.handler)		
		p.parse (data)		
		p.close ()
		return self.handler.get_parsed ()
	
	def close (self):
		pass
			
		
def build_parser ():
	handler = HtmlStripHandler ()
	return Parser (handler)


if __name__ == "__main__":
	import urllib.request, urllib.parse, urllib.error
	p = build_parser ()	
	url = "http://www2.openfos.com/search/key.stk.sk_3com%20switches.htm"
	f = urllib.request.urlopen (url)
	html = f.read ()
	print(p.parse (html))
	
		
	