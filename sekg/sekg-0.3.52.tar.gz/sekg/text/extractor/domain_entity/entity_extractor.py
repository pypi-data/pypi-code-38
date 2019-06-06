#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re

import spacy
from bs4 import BeautifulSoup
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet as wn, stopwords
from sekg.util.code import CodeElementNameUtil


class EntityExtractor(object):
    def __init__(self):
        self.nlp = spacy.load('en')

        hyphen_re = re.compile(r"[A-Za-z\d]+-[A-Za-z\d]+|'[a-z]+|''")
        prefix_re = spacy.util.compile_prefix_regex(self.nlp.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(self.nlp.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(self.nlp.Defaults.suffixes)
        self.nlp.tokenizer = spacy.tokenizer.Tokenizer(self.nlp.vocab, prefix_search=prefix_re.search,
                                                       infix_finditer=infix_re.finditer,
                                                       suffix_search=suffix_re.search, token_match=hyphen_re.match)
        self.pattern = re.compile(r"NP_\w+ of NP_\w+")
        self.stopwords = stopwords.words('english')
        self.stopwords.append("-PRON-")
        self.stopwords = set(self.stopwords)
        self.lemmatizer = WordNetLemmatizer()

        self.code_patterns = [
            re.compile(r'^(?P<ELE>[a-zA-Z0-9_]*[a-z0-9][A-Z][a-z]+[a-zA-Z0-9_]*)(<.*>)?$'),
            re.compile(r'^(?P<ELE>[a-zA-Z0-9_\.<>]+)\([a-zA-Z0-9_\,.<>)]*?$'),
            re.compile(r'^(?P<ELE>[a-zA-Z]{2,}(\.[a-zA-Z0-9_]+)+)(<.*>)?$')
        ]

        self.camel_cache = {}
        self.CODE_NAME_UTIL = CodeElementNameUtil()

    def uncamelize(self, camel_case):
        if camel_case in self.camel_cache:
            return self.camel_cache[camel_case]
        sub = self.CODE_NAME_UTIL.uncamelize_by_stemming(camel_case)
        self.camel_cache[camel_case] = sub
        return sub

    def extract_from_sentence(self, sent):
        """
        extract concept from one sentence.
        :param sent:
        :return: a set of concepts.
        """
        code_elements = self.extract_code_element(sent)

        domain_terms = set()
        doc = self.nlp(sent)
        for chunk in doc.noun_chunks:
            # print("chunk: ", chunk.text)
            chunk = self.clean_chunk(chunk)
            # print("cleaned chunk:", chunk)
            if len(chunk) == 0:
                continue
            if len(chunk) == 1 and self.is_word_common(chunk.text):
                continue
            if chunk.text in code_elements:
                continue
            domain_terms.add(self.chunk_lemmatize(chunk))
            domain_terms.update(self.extract_abbreviation_from_chunk(chunk))
            domain_terms.update(self.extract_NNPs_from_chunk(chunk))
        domain_terms.update(self.extract_np_of_np(doc))
        # print('sent: ' + sent)
        # print('result: ', result)
        domain_terms = self.post_process(domain_terms)
        return domain_terms, code_elements

    def extract_code_element(self, sent):

        elements = set()
        for word in sent.split():
            word = word.lstrip("#(").rstrip(",;.!?")
            for pattern in self.code_patterns:
                search_rs = pattern.search(word)
                if search_rs is not None:
                    elements.add(search_rs.group("ELE"))
        return elements

    def extract_np_of_np(self, doc):
        result = set([])
        sentence_text = doc[:].lemma_
        for chunk in doc.noun_chunks:
            chunk_arr = []
            chunk = self.clean_chunk(chunk)
            if len(chunk) == 0:
                continue
            for token in chunk:
                chunk_arr.append(token.lemma_)
            chunk_lemma = " ".join(chunk_arr)
            # print("chunk_lemma", chunk_lemma)
            replacement_value = "NP_" + "_".join(chunk_arr)
            # print("replacement_value", replacement_value)
            sentence_text = sentence_text.replace(chunk_lemma, replacement_value)
        # print("sentence_text", sentence_text)
        matches = re.findall(self.pattern, sentence_text)
        if len(matches) > 0:
            # print('matched: ', matches)
            for m in matches:
                result.add(m.replace("NP_", "").replace("_", " "))
        return result

    def clean_chunk(self, chunk):
        """
        remove the stopwords, digits and pronouns at the start of the chunk.
        pass the result which contains invalid symbol.
        :param chunk:
        :return:
        """
        if chunk.text.lower() in self.stopwords:
            return []
        while len(chunk) > 1:
            start_token = chunk[0]
            if start_token.text.lower() in self.stopwords or start_token.text.isdigit() or start_token.tag_ == 'PRP':
                chunk = chunk[1:]
            else:
                break
        if len(chunk) == 1:
            start_token = chunk[0]
            if start_token.text.lower() in self.stopwords or start_token.text.isdigit() or start_token.tag_ == 'PRP':
                return []
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\' -]*[a-zA-Z0-9]$', chunk.text):
            return []
        return chunk

    def is_word_common(self, word):
        """
        check if the word is common word.
        :param word:
        :return:
        """
        if word in self.stopwords:
            return True
        if re.match(r'[a-zA-Z]+[a-zA-Z]$', word):
            word = self.lemmatizer.lemmatize(word, pos='n')
            synset = wn.synsets(word)
            if len(synset) > 0:
                return True
            else:
                return False
        return False

    def extract_abbreviation_from_chunk(self, chunk):
        result = set([])
        for token in chunk:
            if re.match(r'[A-Z]{2,}[0-9]*$', token.text):
                result.add(token.text)
        return result

    def extract_NNPs_from_chunk(self, chunk):
        result = set([])
        p = 0
        while p < (len(chunk) - 1):
            if chunk[p].tag_.startswith('NNP'):
                for i in range(p + 1, len(chunk)):
                    if not chunk[i].tag_.startswith('NNP'):
                        t_w = chunk[p:i]
                        p = i
                        if len(t_w) > 1:
                            result.add(self.chunk_lemmatize(t_w))
                        break
                    elif i == len(chunk) - 1:
                        t_w = chunk[p:]
                        p = i
                        if len(t_w) > 1:
                            result.add(self.chunk_lemmatize(t_w))
                        break
            else:
                p = p + 1
        return result

    def chunk_lemmatize(self, chunk):
        """
        lemmatize the last word of chunk.
        :param chunk:
        :return:
        """
        return " ".join([t.lemma_ for t in chunk])

    def post_process(self, result):
        new_result = set([])
        for item in result:
            if len(item) == 1 or item.isdigit():
                continue
            new_result.add(item)
        return new_result

    def extract_from_comment(self, comment):
        """
        extract domain_terms, code_elements from comment text
        :param comment:
        :return:
        """
        comment = re.sub(r'\s+', ' ', comment.strip().strip("/*").strip())
        if len(comment) == 0:
            return set(), set()
        domain_terms, code_elements = self.extract_from_sentence(comment)
        return domain_terms, code_elements

    def extract_from_html(self, html):
        terms = set()
        soup = BeautifulSoup(html, "lxml")
        tts = {tt.get_text() for tt in soup.findAll("tt")}
        terms.update({tt for tt in tts if len(tt.split()) <= 3})
        sent = soup.get_text()
        sent = re.sub(r'\s+', ' ', sent.strip().strip("/*").strip())
        domain_terms, code_elements = self.extract_from_sentence(sent)
        for term in domain_terms:
            terms.add(term)
        return terms, code_elements
