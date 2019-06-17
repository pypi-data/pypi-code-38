import string
from tetumnlp.lexicon import Lexicon
from tetumnlp.tokenizer import Tokenizer

class Translater:

	def __init__(self, lexicon = None):

		if lexicon:
			self.lexicon = lexicon
		else:
			self.lexicon = Lexicon()

		self.tokenizer = Tokenizer(self.lexicon)

	def eng_to_tet(self, text):
		
		words = text.split()

		translated = []

		for word in words:
			found = False
			word_nopunc = word.strip(string.punctuation).strip()
			for entry in self.lexicon.dictionary:
				definitions = self.lexicon.get_definitions(entry["english"])
				for definition in definitions:
					if definition == word_nopunc.lower():
						translated.append({
							"english": word,
							"tetum": word.replace(word_nopunc,entry["tetum"]), #cheat to keep punctuation
							"entry": entry
						})
						found = True
						break
				if found:
					break
			if not found:
				translated.append({
					"english": word.replace(word_nopunc, "[" + word_nopunc + "]"),
					"tetum": None,
					"entry": None
				})
		
		output = ""
		for item in translated:
			if item["tetum"] is not None:
				output+= item["tetum"] + " "
			else:
				output += item["english"] + " "

		return output.strip()


	def tet_to_eng(self, text):

		translated_sentences = []
		sentences = self.tokenizer.get_sentences(text)
		for sentence in sentences:
			words = self.tokenizer.get_tokens(sentence)
			translated_sentence = []
			for word in words:
				if word["english"] is not None:
					definition = self.tokenizer.lexicon.get_first_definition(word["english"])
					translated_sentence.append(definition)
				else:
					translated_sentence.append(word["tetum"])	
			translated_sentences.append(" ".join(translated_sentence))

		output = ""
		for output_sentence in translated_sentences: #hacking whitespace on punctuation
			if len(output_sentence) == 1:
				output+=output_sentence[0]
			else:
				output += " " + output_sentence

		return output.strip()