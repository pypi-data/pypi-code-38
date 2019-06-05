import types
from . import querylexer

PLUS = '+'
MINUS = '-'
TIMES = '*'
DIVIDE = '/'
LPAREN = '('
RPAREN = ')'
EOF = 'EOF'

class ArithmeticParser:
	"""Parses a token list and returns a nested expression structure in
	prefix form."""
	def __init__(self, tokens):
		self.tokens = tokens


	def peek_token(self):
		"""Looks at the next token in our token stream."""
		return self.tokens[0]
		
	def consume_token(self):
		"""Pops off the next token in our token stream."""
		next_token = self.tokens[0]
		del self.tokens[0]
		return next_token


	def parse_expression(self):
		"""Returns a parsed expression.  An expression may consist of a
		bunch of chained factors."""
		expression = self.parse_factor()
		while True:
			if self.peek_token() in (PLUS, MINUS):
				operation = self.consume_token()
				factor = self.parse_factor()
				expression= [operation, expression, factor]
			else: break

		return expression


	def parse_factor(self):
		"""Returns a parsed factor.	A factor may consist of a bunch of
		chained terms."""
		factor = self.parse_term()
		while True:
			if self.peek_token() in (TIMES, DIVIDE):
				operation = self.consume_token()
				term = self.parse_term()
				factor = [operation, factor, term]
			else: break
		return factor

	def parse_term(self):
		"""Returns a parsed term.  A term may consist of a number, or a
		parenthesized expression."""
		if self.peek_token() not in (LPAREN,):
			return str(self.consume_token())
		else:
			self.consume_token() ## eat up the lparen
			expression = self.parse_expression()
			self.consume_token() ## eat up the rparen
			return expression



def main():
	"""Some test code."""
	a= '((alltitle:"medical^3 service" -monitoring) or ("medical^3 service" -monitoring) or (alltitle:"service^3 medical" -monitoring) or ("service^3 medical" -monitoring))'
	b= '(alltitle:"medical^3 service" -monitoring) file:"adada sada" -file:"qwe-qwe-q"'
	c= '((ground range:2123) or (service)) range:2342'
	tokens = querylexer.QueryLexer (b).tokenize ()

	#print tokens	
	expression = ArithmeticParser(tokens).parse_expression()
	print(expression)


if __name__ == '__main__':
	main()
