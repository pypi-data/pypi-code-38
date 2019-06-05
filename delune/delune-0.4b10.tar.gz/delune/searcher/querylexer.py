PLUS = '+'
MINUS = '-'
TIMES = '*'
DIVIDE = '/'
LPAREN = '('
RPAREN = ')'
EOF = 'EOF'
SOP = {"and": TIMES, "not": MINUS, "or": PLUS}

class QueryLexer:
	def __init__ (self, stream, allow_or = 1):
		self.stream = stream.strip ()
		self.allow_or = allow_or
		self.length = len (self.stream)
		self.pos = 0
		self.tokens = []
		self.token = ""
		self.field = None
		self.lparens = 0
		self.rparens = 0
	
	def addParen (self, pa):
		if pa == LPAREN:
			self.lparens += 1
			
		elif pa == RPAREN:
			self.rparens += 1
			if self.rparens > self.lparens:
				self.rparens -= 1
				return
		
		if pa == LPAREN:
			if not self.tokens:
				self.tokens.append (LPAREN)
				return
				
			if self.tokens [-1] == RPAREN or self.tokens [-1] not in (PLUS,MINUS,TIMES,DIVIDE):
				self.addOperator (TIMES)
				self.tokens.append (LPAREN)
				return
			
			self.tokens.append (LPAREN)	
				
		elif pa == RPAREN:
			if not self.tokens:
				self.rparens -= 1
				return
			
			if self.tokens [-1] in (LPAREN,):
				del self.tokens [-1]
				self.lparens -= 1
				self.rparens -= 1
				return # no token in parens
			
			if self.tokens [-1] in (PLUS,MINUS,TIMES,DIVIDE):
				del self.tokens [-1]	
			
			self.tokens.append (RPAREN)
			
	def addOperator (self, op):
		if not self.tokens and op == MINUS: 
			raise ValueError #disallowed - operator
		elif not self.tokens: 
			return	
			
		if self.tokens [-1] == LPAREN: return
		if self.tokens [-1] in (PLUS,MINUS,TIMES,DIVIDE):
			if op == TIMES: return # maybe space
			self.tokens [-1] = op # than replace new operand
		else:				
			self.tokens.append (op)
			
	def addToken (self):
		self.token = self.token.strip ()
		if not self.token: return
		if self.token in SOP:
			self.addOperator (SOP [self.token])
			self.token = ""
			return
		
		if self.tokens and self.tokens [-1] not in (PLUS,MINUS,TIMES,DIVIDE):
			self.addOperator (TIMES)
			
		if self.field:
			if self.field [:3] == "all":
				self.tokens.append (self.field [3:] + ":" + self.token)
			elif self.field [-4:] == "_all":	
				self.tokens.append (self.field [-4:] + ":" + self.token)
			else:
				self.tokens.append (self.field + ":" + self.token)	
		else:	
			self.tokens.append (self.token)
				
		self.token = ""
	
	def setField (self):
		self.field = self.token
		self.token = ""
	
	def unsetField (self):
		self.field = ""
	
	def readPhrase (self):
		self.token = "`"
		while self.pos < self.length:
			c = self.stream [self.pos]
			if c == '\\':
				if self.pos < self.length - 1 and self.stream [self.pos + 1] == '"':
					self.token += '"'
					self.pos += 2
				else:	
					self.token += '\\'
					self.pos += 1					
				
			elif c == '"':
				self.pos += 1
				break
			
			else:	
				self.token += c		
				self.pos += 1
		
		self.addToken ()
			
	def readField (self):
		self.setField ()
		self.addParen (LPAREN)
		
		while self.pos < self.length:
			c = self.stream [self.pos]
			if c == '"' and not self.token:
				self.pos += 1
				self.readPhrase ()				
			
			elif c in ",+":
				self.addToken ()
				self.addOperator (PLUS)
				self.pos += 1
			
			elif c in " ()":
				self.addToken ()
				break
									
			else:
				self.token += c
				self.pos += 1
			
		self.addToken ()
		if self.field [:3] != "all" and self.field [-4:] != "_all":
			self.unsetField ()
			
		self.addParen (RPAREN)
					
	def tokenize (self):		
		while self.pos < self.length:		
			c = self.stream [self.pos]
			if c == '"':
				self.pos += 1
				self.readPhrase ()
			
			elif c == ':':
				if self.token:
					self.pos += 1
					self.readField ()
				else:
					self.pos += 1
					self.addToken ()				
			
			elif c == "/":
				if self.token:
					self.token += c
				self.pos += 1	
					
			elif c in "-+":
				if self.pos == 0 or self.stream [self.pos - 1].isspace ():
					self.pos += 1
					self.addToken ()
					if c == "+": 
						self.addOperator (PLUS)
					else:
						self.addOperator (MINUS)
				else:
					self.token += c
					self.pos += 1
		
			elif c in "()":
				self.pos += 1
				self.addToken ()
				self.addParen (c)
				self.unsetField ()
			
			elif c == " ":
				self.pos += 1
				self.addToken ()
				self.addOperator (TIMES)
				
			else:
				self.token += c
				self.pos += 1
		
		# finally
		self.addToken ()
		while 1:
			if not self.tokens: break
			if self.tokens [-1] in (LPAREN,PLUS,MINUS,TIMES,DIVIDE):
				self.tokens = self.tokens [:-1]
			else:
				break	
		
		for i in range (self.lparens - self.rparens):
			self.tokens.append (RPAREN)		
		
		self.tokens.append (EOF)		
		return self.tokens


class TermLexer (QueryLexer):	
	def addToken (self):
		self.token = self.token.strip ()		
		if not self.token: return
		
		self.tokens.append (self.token)				
		self.token = ""
				
	def addNear (self):
		if self.tokens and self.tokens [-1].find ("^") != -1:
			return
			
		self.tokens.append (self.token)
		self.token = ""
		
	def readNear (self):
		self.token = "^"
		while self.pos < self.length:
			c = self.stream [self.pos]
			if c.isdigit ():
				self.token += c
				self.pos += 1
			
			else:
				break
		
		if len (self.token) > 1:
			self.addNear ()
		else:
			self.token = ""	
		
	def tokenize (self):
		while self.pos < self.length:
			c = self.stream [self.pos]
			if c == "^":
				self.addToken ()
				self.pos += 1
				self.readNear ()
			
			elif c.isalnum () or c in "-/+#*|" or ord (c) > 127:
				self.token += c
				self.pos += 1
			
			else:
				self.addToken ()
				self.pos += 1
		
		self.addToken ()
		self.tokens = [x.strip () for x in self.tokens]
		self.tokens = [x for x in self.tokens if x not in (PLUS,MINUS,TIMES,DIVIDE)]
		
		while 1:
			if not self.tokens: break
			if self.tokens and self.tokens [-1].find ("^") != -1:
				self.tokens = self.tokens [:-1]
			else:
				break
						
		return self.tokens
	
if __name__ == "__main__":
	f = QueryLexer (
		'home:56.14343/-4.1~10.45'
	)	
	print(f.tokenize ())
	
			
		
	