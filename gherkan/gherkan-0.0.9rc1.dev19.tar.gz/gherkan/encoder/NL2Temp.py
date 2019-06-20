# -*- coding: utf-8 -*-
"""
This class aligns natural language phrases into their most default forms and matches them
with niceStr parameters located in templates_dic.yaml. Returns an dict with selected template and
filled as many fields from the dic as possible.
"""
import re, os, imp

from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.utils.word_morpho import Finetuner
from pattern.en import parse, parsetree, lemma, tag
import majka, yaml, string
import pkg_resources, json
import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c
from gherkan.utils import logging_types
import logging

GENERAL_YAML_DIR = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "en-cz_phrases.yaml")

class NLTempMatcher():
    def __init__(self, lang, nmm : NLPModelManager, feature: str):
        self.actor_uni = feature
        self.finetune = Finetuner(lang, nmm)
        self.NLPhrase = None
        self.lang = lang
        self.subj_of_interest = c.SUBJ_OF_INTEREST
        self.program_dic = self.load_program_dic()
        self.morph_wlt = self.finetune.morph_wlt

    def get_NLPhrase(self, phrase):
        phrase = self.remove_passive(phrase)
        negative = self.get_negative(phrase)
        force, unforce = self.get_force_unforce(phrase)
        state, phrase = self.get_state(phrase)
        value = self.get_value(phrase)
        clean_phrase = self.get_cleanphr(phrase, negative, force, unforce)
        if self.lang == "en":
          clean_phrase = self.lemmatize(clean_phrase)
        pn = self.get_pn(clean_phrase)
        if pn:
            clean_phrase = pn
            clean_phrase = self.make_spec_upper(clean_phrase)
        else:
            clean_phrase = self.lemmatize(clean_phrase)
            clean_phrase = self.make_spec_upper(clean_phrase)
            clean_phrase = self.finetune.strip_extra_spaces(clean_phrase)
        clean_phrase = self.finetune.strip_extra_spaces(clean_phrase)
        self.NLPhrase = {"tempToNL": clean_phrase,
                         "negate": negative,
                         "force": force,
                         "unforce": unforce,
                         "state": state,
                         "value" : value
                         }
        return self.NLPhrase

    def remove_passive(self, phrase):
        if self.lang == "en":
            if " ".join(["by", self.subj_of_interest]) in phrase.lower():  # handle passive verb form
                tree = parsetree(phrase, tokenize=True, tags=True,
                                 chunks=True, relations=True)
                for x in tree:  # now we select sentences with robot subjects or passive form
                    if " ".join(["by", self.subj_of_interest]) in x.string.lower():  # handle passive verb form
                        verbs, nouns = ([] for i in range(2))
                        verb_object = (x.string).split(" by ")[0]
                        subject = (x.string).split(" by ")[1]
                        for chunk in x.chunks:
                            if chunk.type == "VP":
                                for word in chunk.words:
                                    verbs.append(
                                        (lemma(word.string)))
                                if "be" in verbs:
                                    verbs.remove("be")
                                rest = verb_object.replace(chunk.string, "")
                        sent = subject + " " + ' '.join(verbs) + " " + rest
                        phrase = sent.translate(
                            str.maketrans('', '', string.punctuation))
        elif self.lang == "cs":
            pass

        return phrase

    def make_spec_upper(self, sent):
        """e.g. shuttle xy > shuttle XY"""
        if self.lang == "en":
            tree = parsetree(sent, tokenize=True, tags=True, chunks=True, relations=True)
            for sentence in tree:
                actors = sentence.nouns
            if actors:
                for actor in actors:
                    spec = re.findall(r'{}\s+([A-Za-z0-9]{})\b'.format(actor.string,"{1,3}"), sent)
                    if spec:
                        for n in spec:
                            for word, pos in tag(n):
                                if pos == "NN" or pos == "NNP" or pos == "RB":
                                  sent = str(re.sub(r'\b({})\b'.format(n), n.upper(), sent))
        elif self.lang == "cs":
           nouns = []
           for word in sent.split():
            word_info = self.finetune.get_txt_info(word)
            if (word_info[0]["pos"]) == "N" and (word_info[0]["pos_det"]) == "N":
                nouns.append(word)
            for noun in nouns:
                if len(noun) <= 3:
                    sent = re.sub(r'\b{}\b'.format(noun), noun.upper(), sent)
        return sent

    def get_pn(self, phrase):
        actor = re.findall(r'{}\s+([A-Za-z0-9]{})\b'.format(self.subj_of_interest,"{1,2}"),
                           phrase, re.IGNORECASE)
        if not actor:
            actor_ori = self.subj_of_interest
            if self.subj_of_interest in self.actor_uni and self.subj_of_interest in phrase:
                actor = self.actor_uni
            elif self.subj_of_interest not in self.actor_uni:
                # logging.warning("Feature does not contain {}, cannot resolve phrase {}".format(self.subj_of_interest, phrase))
                actor = self.actor_uni
        else:
            actor = " ".join([self.subj_of_interest, actor[0]])
            actor_ori = actor
        verb = self.finetune.find_verb(self.lang, phrase)
        if verb:
            verb_lemma = self.finetune.lemmatize(self.lang, verb[0])
            phrase = re.sub(verb[0], verb_lemma, phrase)
        action_lemma = re.sub(r'\b{}\b'.format(actor_ori), "", phrase, re.IGNORECASE)
        action_lemma = self.lemmatize(action_lemma)
        if not actor:
            return False
        if actor.lower() in self.program_dic.keys():
            action_lemma = "".join(action_lemma.lower().rsplit(actor.lower()))
            action_lemma = self.finetune.lemmatize_sentence(self.lang, action_lemma)
            for key in self.program_dic[actor.lower()]:
                if self.finetune.strip_extra_spaces(action_lemma.lower()) == self.program_dic[actor.lower()][key].lower():
                    actor_l = actor.split()
                    actor = " ".join([actor_l[0], actor_l[1].upper()])
                    phrase = "{} #{}".format(actor, key) # internal format for program numbers in NL
                    return phrase
        elif actor.lower() == self.subj_of_interest:  # if no specification, use the one defined in Feature
            for key in self.program_dic:
                action_lemma = self.finetune.lemmatize_sentence(self.lang, action_lemma)
                for value in self.program_dic[key]:
                 if self.finetune.strip_extra_spaces(action_lemma) == self.program_dic[key][value]:
                    phrase = "{} #{}".format(key, value) # internal format for program numbers in NL
                    return phrase
        return False

    def translate(self, phrase):
        new_phrase = phrase
        with open(GENERAL_YAML_DIR, 'r', encoding="utf-8") as stream:
            try:
                vocab = yaml.full_load(stream)
            except:
                logging.debug("Could not load en-cz_phrases {}", GENERAL_YAML_DIR)
        for word in phrase.split():
            for key in vocab["cs"]:
                word_en = ""
                if isinstance(vocab['cs'][key], list):
                   for x in vocab['cs'][key]:
                      if word.lower() == x:
                          word_en = key
                elif word.lower() == vocab['cs'][key]:
                  word_en = key
                if word_en:
                    new_phrase = re.sub(r'\b{}\b'.format(word), word_en, new_phrase, re.IGNORECASE)
        return new_phrase

    def get_state(self, phrase):
        # TODO infinitive should be enough if the phrases are lemmatized
        stop_phrases=["end", "ends", "ended", "ending", "finish", "finishes", "stops", "finished", "stopped",
                      "stop", "skončit", "dokončit", "přestat", "-skončit", "-dokončit", "end", "finish", "do start"]
        start_phrases=["start", "starts", "started", "starting", "začít"]
        for word in phrase.split():
                if self.finetune.lemmatize(self.lang, word).lower() in stop_phrases:
                   if word == phrase.split()[-1] or phrase.split()[-1] == "program":
                       break
                   phrase = re.sub(word, '', phrase, re.IGNORECASE)
                   state = "End"
                   return state, phrase
                elif self.finetune.lemmatize(self.lang, word).lower() in start_phrases:
                    if word == phrase.split()[-1]:
                        break
                    phrase = re.sub(word, '', phrase, re.IGNORECASE)
                    state = "Start"
                    return state, phrase
        state = None
        return state, phrase


    def get_value(self, phrase):
        # TODO only a stub
        # this method should discover value in the phrase which is stated only implicitly, i.e. which is not in the template

        value = None
        zero_value_phrases = ["empty", "prázdný"]

        for word in phrase.split():
            if self.finetune.lemmatize(self.lang, word).lower() in zero_value_phrases:
                value = 0

        return value


    def get_force_unforce(self, phrase):
        if self.lang == 'en':
           force = re.findall(r'\b(force)\b', phrase, re.IGNORECASE)
           unforce = re.findall(r'\b(unforce)\b', phrase, re.IGNORECASE)
        elif self.lang == 'cs':
            no_diacritics = self.finetune.remove_diacritics(phrase)
            force = re.findall(r'\b({}|{})\b'.format("Vynut", "Vynutit"), no_diacritics, re.IGNORECASE)
            unforce = re.findall(r'\b({})\b'.format("Uvolni", "Uvolnit"), no_diacritics, re.IGNORECASE)
        if not self.empty_tree(force):
            force = True
        else:
            force = False
        if not self.empty_tree(unforce):
            unforce = True
        else:
            unforce = False
        return force, unforce

    def get_negative(self, phrase):
        verbs = self.finetune.find_verb(self.lang, phrase)
        if self.lang == "en":
            if verbs:
                for verb in verbs:
                    negative = re.findall(r'\b(not)\b\s+\b({})\b|(\b({})\b)\s\b(not)\b'.format(verb, verb), phrase)
                    if not self.empty_tree(negative):
                        negative = True
                    else:
                        negative = False
            else:
                negative = False
        elif self.lang == "cs":
            negative = False
            verbs = self.finetune.find_verb(self.lang, phrase)
            if verbs:
                for verb in verbs:
                    verb_info = self.finetune.get_txt_info(verb)
                    if verb_info[0]["negate"] == "N":
                        negative = True
        return negative

    def get_cleanphr(self, phrase, negative=None, force=None, unforce=None):
        # clean the phrase from negatives and force
        del_words = ["do", "does", "will", "can", "must", "have to"]
        if self.lang == "en":
            if negative:
              phrase = re.sub(r'\b(not)\b', '', phrase, re.IGNORECASE)
              for i in del_words:
                phrase = re.sub(r'\b({})\b'.format(i), "", phrase)
                phrase = self.finetune.strip_extra_spaces(phrase)
            if force:
              phrase = re.sub(r'\b(force)\b', '', phrase, re.IGNORECASE)
            if unforce:
                phrase = re.sub(r'\b(unforce)\b', '', phrase, re.IGNORECASE)
            # remove excess verb words
        elif self.lang == "cs":
            if force:
              phrase = re.sub(r'\b({}|{}|{})\b'.format("vynuť", "vynut", "vynutit"), '', phrase, re.IGNORECASE)
            if unforce:
                phrase = re.sub(r'({})\b'.format("uvolni", "uvolnit"), '', phrase, re.IGNORECASE)
            if negative:
                verbs = self.finetune.find_verb(self.lang, phrase)
                if verbs:
                    for verb in verbs:
                        verb_info = self.finetune.get_txt_info(verb)
                        if verb_info[0]["negate"] == "N":
                            infinitive = self.finetune.lemmatize(self.lang, verb).split("-")
                            if infinitive:
                              verb_infinitiv = "".join(string for string in infinitive if len(string) > 0)
                              verb_new = re.sub(r"^(ne)", "", verb_infinitiv, re.IGNORECASE)
                              phrase = re.sub(verb, verb_new, phrase, re.IGNORECASE)
                            else:
                                verb_new = re.sub(r"^(ne)","", verb, re.IGNORECASE)
                                phrase = re.sub(verb, verb_new, phrase, re.IGNORECASE)

        phrase = self.finetune.strip_extra_spaces(phrase)
        return phrase

    def empty_tree(self, input_list):
        """Recursively iterate through values in nested lists."""
        for item in input_list:
            if not isinstance(item, list) or not self.empty_tree(item):
                return False
        return True

    def lemmatize(self, text):
        with pkg_resources.resource_stream("gherkan", "utils/verbs.yaml") as stream:
            verb_dic = yaml.full_load(stream)
        with pkg_resources.resource_stream("gherkan", "utils/lemma_exceptions.yaml") as stream:
            lemma_dic = yaml.full_load(stream)
        lemmas = ""
        skip_list = [",", ".", ";"]
        if self.lang == "cs":
            verb = self.finetune.find_verb(self.lang, text)
            if verb:
                for key in verb_dic[self.lang]["verbs"]:
                    if verb[0] in key.keys():
                        verb_lemma = key[verb[0]]
                        text = re.sub(r'\b{}\b'.format(verb[0]), verb_lemma, text, re.IGNORECASE)
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

    def load_program_dic(self):
        # load program json
        program_dic = {}
        if self.lang == "en":
            file = "utils/RobotPrograms_en.json"
        elif self.lang == "cs":
            file = "utils/RobotPrograms_cs.json"
        with pkg_resources.resource_stream("gherkan", file) as stream:
            try:
                program_dic = json.load(stream)
            except:
                logging.debug("Could not load {}", file)
        return program_dic

