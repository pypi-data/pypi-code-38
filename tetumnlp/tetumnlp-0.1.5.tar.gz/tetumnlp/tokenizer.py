import re
import time
from tetumnlp.lexicon import Lexicon

class Tokenizer:

	def __init__(self, lexicon = None):

		if lexicon:
			self.lexicon = lexicon
		else:
			self.lexicon = Lexicon()

	def get_sentences(self, text):

		return list(filter(None, re.split(r'(\.|!|\?)', text)))
		#return list(filter(None, re.split(r'\.|!|\?', text)))	

	def get_tokens(self, sentence):

		tokens = []

		words = sentence.split()
		i = 0
		while i < len(words):
			found = False
			for entry in self.lexicon.dictionary:
				w1 = list(map(str.lower, words[i:i+len(entry["words"])]))
				w2 = list(map(str.lower, entry["words"]))
				if w1 == w2:
					tokens.append(entry)
					i = i+len(entry["words"])
					found = True
					break
			#not found in lexicon
			if not found:
				tokens.append({
					"tetum": words[i],
					"english": None
				})
				i=i+1				

		return tokens
