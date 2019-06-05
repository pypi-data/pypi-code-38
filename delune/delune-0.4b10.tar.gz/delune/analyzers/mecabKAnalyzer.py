"""
Install Mecab and Dictionary
---------------------------------
apt install curl autoconf g++ python3-dev
$ bash < (curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)

https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/
wget https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.0.3-20170922.tar.gz

tar -zxfv mecab-ko-dic-XX.tar.gz
cd mecab-ko-dic-XX
./configure
make
sudo make install

Install JDK for Java morphers
---------------------------------
apt-get install default-jdk

Install konlpy
----------------
pip3 install JPype1-py3 konlpy

(Optional) Change System Locale
---------------------------------
apt install language-pack-ko
sudo locale-gen ko_KR.UTF-8

sudo vi /etc/default/locale   
 - LANG=ko_KR.UTF-8
source /etc/default/locale
"""

from . import standardAnalyzer
import re

class Analyzer (standardAnalyzer.Analyzer):
	defaults = {	
		"strip_html": 0,
		"make_lower_case": 0,
		"stopwords": [],
		"contains_alpha_only": 0,
		"dicpath": '/usr/local/lib/mecab/dic/mecab-ko-dic'
	}
	
	def __init__ (self, max_term = 8, numthread = 1, **karg):
		self.stopwords = {}
		standardAnalyzer.Analyzer.__init__ (self, max_term, numthread, **karg)
		
	def createTSAnalyzers (self, num):
		from konlpy.tag import Mecab
		
		#I don't know Mecab is thread-safe
		for i in range (num):
			self.ats.append (Mecab (self.options.get ("dicpath")))
	
	#------------------------------------------------
	# exported methods
	#------------------------------------------------				
	def index	(self, document, lang = "en"):
		document = self.preprocess (document)
		d = {}
		t = 0
		for pos, term in enumerate (self.ats [self.get_tid ()].morphs (document)):
			if term in self.stopwords:
				continue
			if term not in d:
				d [term] = []
			d [term].append (pos)	
			t += 1
			if t > self.max_term:
				break			
		return d
	
	def tokenize (self, document, lang = "en"):
		if self.options.get ("make_lower_case"):
			document = document.lower ()			
		return [term for term in self.ats [self.get_tid ()].morphs (document) if term not in self.stopwords]
	query = tokenize
	
	def nouns (self, document):
		return self.ats [self.get_tid ()].nouns (document) [:self.max_term]

	def pos (self, document):
		return self.ats [self.get_tid ()].pos (document) [:self.max_term]
		
	def count_stopwords (self, document, lang = "en"):
		document = self.preprocess (document)
		terms = self.tokenize (document)
		c = 0
		for term in terms:
			if term in self.stopwords:
				c += 1
		return c, len (terms)
		
	#------------------------------------------------
	# handle options 
	#------------------------------------------------		
	def set_stopwords (self, wordlist):
		if not wordlist: return
		self.stopwords = dict ([(x, None) for x in wordlist])
			
	def set_endwords (self, wordlist):
		raise AttributeError
	
	def set_stem_level (self, stem_level):
		raise AttributeError
		
	def set_ngram_no_space (self, flag):
		raise AttributeError
	
	def set_stopwords_case_sensitive (self, flag):
		raise AttributeError
				
	def set_ngram (self, ngram):
		raise AttributeError
	
	def set_biword (self, flag):
		raise AttributeError
		