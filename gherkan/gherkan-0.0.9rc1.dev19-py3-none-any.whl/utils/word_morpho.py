# coding: utf-8
# from googletrans import Translator
import majka, re
from pattern.en import conjugate, parsetree, lemma
import spacy, unicodedata
import pkg_resources, yaml

from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.utils.czech_morpho import CZMorph
from gherkan.utils import logging_types
import logging


class Finetuner:
    def __init__(self, lang: str, nmm: NLPModelManager):
        self.nlp_model_en = nmm.nlp_model_en
        self.nlp_model_cs = CZMorph(nmm.nlp_model_cs)
        self.morph_lwt = nmm.morph_lwt
        self.morph_wlt = nmm.morph_wlt

        with pkg_resources.resource_stream("gherkan", "utils/verbs.yaml") as stream:
            self.verb_dic = yaml.full_load(stream)

    def conjugate(self, lang, word, person, number="singular"):
        """  Returns provided noun in given grammatical case / Vrátí podstatné jméno vyskloňované v daném pádu """
        negation = self.get_txt_info(word)[0]["negate"]
        if len(word.split()) > 1:
            return word
        if negation == "A":
            neg = False
        else:
            neg = True
        declenation = ""
        if lang == "en":
           try:
            if number == "singular":
                tag = str(person) + "sg"
                declenation = conjugate(word, tag)
            elif number == "plural":
                tag = str(person) + "pl"
                declenation = conjugate(word, tag)
           except:
               declenation = word
        elif lang == "cs":
           try:
            self.morph_lwt.flags |= majka.ADD_DIACRITICS
            analysis = self.morph_lwt.find(word)
            if analysis == []:
                declenation = word
            if number == "singular":
                for n in range(len(analysis)):
                    if 'singular' in analysis[n]['tags']:
                        declen = [analysis[n]['lemma'], analysis[n]['tags']]
                        if "person" in declen[1]:
                            if declen[1]["person"] == int(person) and declen[1]["singular"] is True and declen[1]["negation"] is neg:
                                declenation = declen[0]
                        elif "case" in declen[1]:
                            if declen[1]["case"] == int(person) and declen[1]["singular"] is True:
                                if "negation" in declen[1] and declen[1]["negation"] is not neg:
                                    pass
                                else:
                                    declenation = declen[0]
                                    break
            else:
                for n in range(len(analysis)):
                    if 'singular' in analysis[n]['tags']:
                        declen = [analysis[n]['lemma'], analysis[n]['tags']]
                        if "person" in declen[1]:
                            if declen[1]["person"] == int(person) and declen[1]["singular"] is False and declen[1]["negation"] is neg:
                                declenation = declen[0]
                        elif "case" in declen[1]:
                            if declen[1]["case"] == int(person) and declen[1]["singular"] is False:
                                declenation = declen[0]
           except:
               declenation = word
        if not declenation:
            declenation = word
        if word == "nebýt" and person == 3:   # majka does not work for this case
            if number == "singular":
                declenation = "není"
            else:
                declenation = "nejsou"
        return declenation

    def start_sentence_upper(self, text):
        """Changes the letters at the beginning of sentences into upper"""
        return re.sub("(^|[.?!])\s*([a-zA-Z])", lambda p: p.group(0).upper(), text.lower())

    def strip_extra_spaces(self, text):
        stripped_spaces = re.sub(' +', ' ', text)
        stripped_text = stripped_spaces.strip()
        return stripped_text

    def lemmatize(self, lang, word):
        """  Returns lemma of given word form / Vrátí základní podobu slova (např. infinitiv)"""
        lemma = word
        if lang == "cs":
            verb = self.find_verb(self.lang, word)
            if verb:
                for key in self.verb_dic[self.lang]["verbs"]:
                    if verb[0] in key.keys():
                        lemma = key[verb[0]]
                        return lemma
            self.morph_wlt.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
            self.morph_wlt.tags = False  # return just the lemma, do not process the tags
            self.morph_wlt.first_only = True  # return only the first entry
            output = self.morph_wlt.find(word)
            if output:
              lemma = output[0]['lemma']
        else:
            doc = self.nlp_model_en(word)
            for token in doc:
                    lemma = str(token.lemma_)

        return lemma

    def lemmatize_sentence(self, lang, text):
        with pkg_resources.resource_stream("gherkan", "utils/verbs.yaml") as stream:
            verb_dic = yaml.full_load(stream)
        with pkg_resources.resource_stream("gherkan", "utils/lemma_exceptions.yaml") as stream:
            lemma_dic = yaml.full_load(stream)
        self.lang = lang
        lemmas = ""
        skip_list = [",", ".", ";"]
        if self.lang == "cs":
            self.morph_wlt.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
            self.morph_wlt.tags = False  # return just the lemma, do not process the tags
            self.morph_wlt.first_only = True  # return only the first entry
            for word in text.split():
               if word in skip_list:
                   pass
               else:
                   found = False
                   for key in lemma_dic[self.lang]:
                       for keyword in lemma_dic[self.lang][key]:
                           if word.lower() == keyword:
                               lemmas += " "
                               lemmas += key
                               found = True
                               break
                   if not found:
                       output = self.morph_wlt.find(word)
                       lemmas += " "
                       if output:
                           lemma_det = output[0]['lemma']
                           lemmas += lemma_det
                       else:
                           lemmas += word



        elif self.lang == "en":
            # this version keeps capitals
            tree = parsetree(text, tokenize=True)

            for sentence in tree:
                for word in sentence:
                    if word.string in skip_list:
                        pass
                    found = False
                    for key in lemma_dic[self.lang]:
                        for keyword in lemma_dic[self.lang][key]:
                            if word.string.lower() == keyword:
                                lemmas += " "
                                lemmas += key
                                found = True
                                break
                    if not found:
                        lemmas += " "
                        lemmas += lemma(word.string)

        return lemmas

    def change_case(self, word, case, plural = False):
        """  Returns provided noun in given grammatical case / Vrátí podstatné jméno vyskloňované v daném pádu """
        self.morph_lwt.flags |= majka.ADD_DIACRITICS
        word_form = []
        analysis = self.morph_lwt.find(word)

        if plural == False:
            for n in range(len(analysis)):
                if 'singular' in analysis[n]['tags']:
                    declen = [analysis[n]['lemma'],analysis[n]['tags']['case']]
                    if case in declen:
                       word_form.append(declen[0])
                else:
                    pass
        else:
            for n in range(len(analysis)):
                if 'plural' in analysis[n]['tags']:
                    declen = [analysis[n]['lemma'], analysis[n]['tags']['case']]
                    if case in declen:
                        word_form.append(declen[0])
            else:
                pass

        return word_form[0]

    def make_negative(self, lang, word):
        if lang == "cs":
            self.morph_wlt.flags |= majka.ADD_DIACRITICS
            self.morph_wlt.tags = False
            self.morph_wlt.first_only = False
            analysis = self.morph_wlt.find(word)
        elif lang == "en":
            neg = conjugate(word, negated=True)

    def get_cases(self, word):
        """ Returns all possible cases of the word, in case of verb returns all info / Vrátí možné pády daného slova, u sloves vrátí všechno info"""
        self.morph_wlt.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
        output = self.morph_wlt.find(word)

        cases = []
        if "substantive" in output[0]['tags']['pos'] or "adjective" in output[0]['tags']['pos']:
            for n in range(len(output)):
                 case = output[n]['tags']['case']
                 if "singular" in output[n]['tags']:
                  number = "singular"
                 else:
                  number = "plural"
                 cases.append([case, number])

        elif "verb" in output[0]['tags']['pos']:
            cases = output

        return cases


    def align_adjectives(self, lang, sentence):
        word_list = sentence.split()
        self.morph_wlt.flags |= majka.ADD_DIACRITICS
        config = []
        if lang =="cs":
            for word in word_list:
                analysis = self.morph_wlt.find(word)
                if analysis == []:
                   continue
                else:
                    if 'tags' in analysis[0]:
                        if analysis[0]["tags"]["pos"] == "substantive":
                            config = analysis[0]["tags"]
                            config["negation"] = False
                            del config["pos"]
                            if 'plural' in config:
                                del config["plural"]
            if config:
                verb = self.find_verb(lang, sentence)
                try:
                   analysis = self.morph_wlt.find(verb[0])
                   config["singular"] = analysis[0]["tags"]["singular"]
                except:
                    pass
                for word in word_list:
                    analysis = self.morph_lwt.find(word)
                    if analysis:
                        if analysis[0]["tags"]["pos"] == "adjective":
                            for dict in analysis:
                                if all(item in dict["tags"].items() for item in config.items()):
                                    aligned_adj = dict["lemma"]
                                    sentence = re.sub(word, aligned_adj, sentence)
        else:
            pass
        return sentence

    def remove_diacritics(self, text):
        """
        Returns a string with all diacritics (aka non-spacing marks) removed.
        For example "Héllô" will become "Hello".
        Useful for comparing strings in an accent-insensitive fashion.
        """
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    def get_txt_info(self, text):
        """For Czech only - get POS tagging from Morphodita"""
        text_info = self.nlp_model_cs.get_pos_info(text)
        return text_info

    def find_verb(self, lang, sentence, head_only=True):
        verb = []
        word_list = sentence.split()
        if lang =="cs":
            for word in word_list:
                analysis = self.morph_wlt.find(word)
                if analysis == []:
                   continue
                else:
                    if 'tags' in analysis[0]:
                        if analysis[0]["tags"]["pos"] == "verb":
                            verb.append(word)
                        else:
                            continue
            if not verb:
                sent_lst = self.nlp_model_cs.get_pos_info(sentence)
                for x in sent_lst:
                    if x["pos"] == "V":
                        verb.append(x["word"])

        elif lang == "en":
            t = parsetree(sentence, tokenize=True,  tags=True)
            excepts = ["start", "stop", "end", "finish"]
            for sent in t:
                  chunk = sent.verbs
                  check = False
                  if chunk:
                      for x in excepts:
                              if x in chunk[0].string:
                                word = re.findall(r'\w*{}\w*'.format(x), chunk[0].string)
                                if word:
                                  verb.append(word[0])
                                  check = True
                      if not check:
                             if head_only:
                               verb.append(chunk[0].head.string)
                             else:
                               verb.append(chunk[0].string)
                  else:
                    for x in t.string.split():
                      if x in excepts:
                          word = re.findall(r'\w*{}\w*'.format(x), t.string)
                          if word:
                              verb.append(word[0])
        sentence_l = self.lemmatize_sentence(lang, sentence)
        if verb:
            verb_copy = verb
            for v in verb_copy:
              if v in self.verb_dic[lang]["not verbs"]:
                verb.remove(v)
              if not verb:
                new_phrase = sentence.replace(v, "")
                self.find_verb(lang, new_phrase)
        if not verb:
            for word in sentence_l.split():
                if word in self.verb_dic[lang]["verbs"]:
                    verb = [word.replace("-", "ne")]
        if not verb:
            logging.debug("Warning: did not detect any verb in sentence: {}", sentence)
        return verb

    # def translate(self, phrase, lang = "cz-en"):
    #     """ Translates a word or phrase from czech to english (lang = "cz-en") or from english to czech (lang = "en-cz") """
    #     translator = Translator()
    #     if lang == "cz-en":
    #       result = translator.translate(phrase, src="cs", dest='en')
    #     elif lang == "en-cz":
    #       result = translator.translate(phrase, src="en", dest='cs')
    #
    #     translation = result.text
    #     return translation



