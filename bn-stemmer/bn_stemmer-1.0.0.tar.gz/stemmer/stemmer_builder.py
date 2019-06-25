import string
import re


class BanglaStemmer:

	punc_dict = {}

	def __init__(self):
		self.punc_dict = {}


	def stem(self, word):
		
		return self.step_a(self.word_cleaner(word))


	def word_cleaner(self, word):

		self.punctuation_manipulator()

		new_word = '';

		for c in word:
			if self.punc_dict.get(c):
				continue
			if c == ' ' or c == '।':
				continue	
			else:
				new_word = new_word + c
		return new_word			

	def punctuation_manipulator(self):
		for c in string.punctuation:
			self.punc_dict[c] = True

	def step_a(self, word):
		if word.endswith('েয়েছিল'):
			return word.replace('েয়েছিল', 'া')
		if word.endswith(('রছ','রব')):
			return word[:-1]
		if word.endswith('েয়ে'):
			return word.replace('েয়ে', 'া')	
		if word.endswith('েয়েছিলেন'):
			return word.replace('েয়েছিলেন', 'া')	
		if word[1] == 'ে' and word[3:11] == 'েছিলেন':
			return word[0] + 'া' + word[2] + 'া'
		if word[1] == 'ে' and word[3] == 'ে':
			return word[0] + 'া' + word[2] + 'া'	
		else:
			return word		
			


x = BanglaStemmer()

items = ['খাচ্ছি','যাচ্ছি','হচ্ছিল','হচ্ছে','যাচ্ছে','যাচ্ছিস','খাচ্ছিস','যাচ্ছিলেন','খাচ্ছিলেন','যাচ্ছ','খাচ্ছ']

for i in items:
	print(x.stem(i))			

'''		
my_dict = {}

file1 = codecs.open('../bn.txt', 'r', 'utf8')
content = file1.read()
words = content.split()

stemmed_words = []

def word_cleaner():
	for x in words:
		if x.endswith('?') or x.endswith('!') or x.endswith(','):
			stemmed_words.append(x[:-1])
		elif x == u'৷':
			continue	
		else:
			stemmed_words.append(x)

def step_c(word):
	if word.endswith(u'চ্ছিলেন'):	
		return word.replace(u'চ্ছিলেন', '')
	elif word.endswith(u'ছিলাম'):
		return word.replace(u'ছিলাম', '')
	elif word.endswith(u'ছিলেন'):
		return word.replace(u'ছিলেন', '')
	elif word.endswith(u'চ্ছিস'):
		return word.replace(u'চ্ছিস', '')	
	elif word.endswith(u'চ্ছিল'):
		return word.replace(u'চ্ছিল', '')	
	elif re.search(u'.ে.েছেন$', word):
		return word[0]+u'া'+word[2]	
	elif word.endswith(u'েছেন'):
		return word.replace(u'েছেন', '')		
	elif word.endswith(u'ছিলে'):
		return word.replace(u'ছিলে', '')		
	elif word.endswith(u'ছিল'):
		return word.replace(u'ছিল', '')
	elif word.endswith(u'ছেন'):
		return word.replace(u'ছেন', '')			
	elif word.endswith(u'বেন'):
		return word.replace(u'বেন', '')								
	elif word.endswith(u'চ্ছ'):
		return word.replace(u'চ্ছ', '')
	#elif re.search(u'.চ্ছি$', word):
	#	return word.replace(u'চ্ছি', u'')
	#elif re.search(u'.চ্ছে$', word):
	#	return word.replace(u'চ্ছে', '')
	elif word.endswith(u'িস'):
		return word.replace('িস', '')
	elif word.endswith(u'ছিস'):
		return word.replace('ছিস', '')
	elif word.endswith(u'ছিলি'):
		return word.replace('ছিলি', '')		
	elif word.endswith(u'েন'):
		return word.replace(u'েন', '')		
	elif word.endswith(u'বে'):
		return word.replace(u'বে', '')
	elif word.endswith(u'ছে'):
		return word.replace(u'ছে', '')								
	elif word[-1] == u'া':
		return word[:-1]
	elif word[-1] == u'ি':
		return word.replace(u'ি', '')								
	else:
		return word

def step_a(word):
	if word.endswith(u'তো'):
		if size_checker(word):
			return word.replace(u'তো', '')
		else:
			return word	
	elif word.endswith(u'ই'):
		if size_checker(word):
			return word.replace(u'ই', '')	
		else:
			return word	
	elif word.endswith(u'ও'):
		if size_checker(word):
			return word.replace(u'ও', '')
		else:
			return word	
	elif word.endswith(u'কে'):
		if size_checker(word):
			return word.replace(u'কে', '')
		else:
			return word	
	elif word.endswith(u'তে'):
		if size_checker(word):
			return word.replace(u'তে', '')
		else:
			return word	
	elif word.endswith(u'রা'):
		if size_checker(word):
			return word.replace(u'রা', '')
		else:
			return word
	elif word.endswith(u'য়'):
		if size_checker(word):
			return word.replace(u'য়', '')
		else:
			return word					
	else:
		return word	

def step_b(word):
	if word.endswith(u'েরগুলোর'):
		return word.replace(u'েরগুলোর', '')
	elif word.endswith(u'েরগুলো'):
		return word.replace(u'েরগুলো', '')
	elif word.endswith(u'গুলোর'):
		return word.replace(u'গুলোর', '')
	elif word.endswith(u'গুলো'):
		return word.replace(u'গুলো', '')
	elif word.endswith(u'েরটার'):
		return word.replace(u'েরটার', '')
	elif word.endswith(u'েরটা'):
		return word.replace(u'েরটা', '')
	elif word.endswith(u'ের'):
		return word.replace(u'ের', '')
	elif word.endswith(u'ে'):
		if size_checker(word):
			return word.replace(u'ে', '')
		else:
			return word		
	elif word.endswith(u'েয়ে'):
		return word.replace(u'েয়ে', u'া')	
	elif word.endswith(u'ার'):
		return word.replace(u'ার', '')		
	elif word.endswith(u'টার'):
		return word.replace(u'টার', '')	
	elif word.endswith(u'টির'):
		return word.replace(u'টির', '')
	elif word.endswith(u'টি'):
		return word.replace(u'টি', '')
	elif word.endswith(u'টা'):
		return word.replace(u'টা', '')
	else:	
		return word

def size_checker(word):
	if len(word) >= 5:
		return True
	else:
		return False	



def stop_words_remover(content):
	stop_words_dict = {}
	words = load_data()
	for word in words:
		stop_words_dict[u''+word] = True

	reform_words = []

	for word in content:
		if stop_words_dict.get(word):
			continue
		else:
			reform_words.append(word)
	return reform_words				


def load_data():
	file1 = codecs.open('bn_stop_words.txt', 'r', 'utf8')
	content = file1.read()
	return content.split()


word_cleaner()		

#for i in stemmed_words:
#	print(verb_rules(i))

n_words = stop_words_remover(stemmed_words)

for word in n_words:
	word = step_a(word)
	word = step_b(word)
	word = step_c(word)
	print(word)

'''
