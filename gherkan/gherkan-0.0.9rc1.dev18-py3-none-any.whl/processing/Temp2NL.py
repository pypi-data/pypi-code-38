# coding: utf-8
"""
Class FillActions turns the filled object SignalPhrase into a natural language phrase, which is then returned
as the filled field niceStr in the SignalPhrase.
"""
import json, os, re
import yaml
from pattern.en import PARTICIPLE, conjugate
import gherkan.utils.constants as c
import gherkan.utils.gherkin_keywords as g
from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.utils.word_morpho import Finetuner
from gherkan.utils import logging_types
import logging

CZ_PROGRAM_DICT_DIR = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "RobotPrograms_cs.json")
EN_PROGRAM_DICT_DIR = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "RobotPrograms_en.json")
GENERAL_YAML_DIR = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "en-cz_phrases.yaml")


class FillActions:
    def __init__(self, nmm : NLPModelManager):
        self.finetune = Finetuner(lang="cs", nmm=nmm)
        self.lang = None

    def ParseMainAction(self, data):
        """ Construct basic NL phrase from given template
            Input format of data:
            data = {Name, Vars, Values, TempToNL}
            Vars = list of strings; specific values to fill into template
            Values = list of integers; values for given Types
            TempToNL = string; specific details for given template
        """
        self.data = self.convert_to_dic(data)
        self.lang = self.data["language"]
        varz = self.data["vars"]
        values = self.data["values"]
        phrase = self.data["tempToNL"][0]
        for key in varz:  # separate actor names (shuttleXY > shuttle XY)
            if not varz[key].isupper():
                string = str(varz[key][1:])  # we leave out the first letter in case it is upper
                actor = (re.findall('([A-Z0-9].*)', string))
                if actor:
                    varz[key] = varz[key].replace(actor[0], " {}".format(actor[0]))
                else:
                    pass
        for key, v in values.items():  # try to match the values with .json
            matched = self.MatchAction(varz['subject'], values[key])
            if matched:
                values[key] = matched
                to_replace = re.compile(r"#\(\?P\<{}\>[^\)]+\)".format(key))
                phrase = re.sub(to_replace, values[key], phrase)
            else:
                if isinstance(values[key], bool):
                  phrase = self.ParseBool(phrase, values[key])
                else:
                    to_replace = re.compile(r"\(\?P\<{}\>[^\)]+\)".format(key))
                    phrase = re.sub(to_replace, values[key], phrase)
        for key, value in varz.items():  # match varz with template
            idx = list(varz).index(key)
            if key == "place":
                value = value + "_2"
            value = self.MatchGeneral(value)
            print(value)
            if self.data["inclinations"][idx] != 0:
                value = self.finetune.conjugate(self.lang, value, self.data["inclinations"][idx])
                print(value)
            to_replace = re.compile(r"\(\?P\<{}\>[^\)]+\)".format(key))
            phrase = re.sub(to_replace, value, phrase)
        verb = self.finetune.find_verb(self.lang, phrase)
        if verb:
            verb_conj = self.finetune.conjugate(self.lang, verb[0], 3) # conjugate verb to third person
            phrase = re.sub(verb[0], verb_conj, phrase)
        for word in phrase.split():
            word_new = self.MatchGeneral(word)  # translate words to czech
            phrase = re.sub(r'\b({})\b'.format(word), word_new, phrase)
        print(phrase)
        phrase = self.finetune.strip_extra_spaces(phrase)
        phrase = self.finetune.align_adjectives(self.lang, phrase)

        if phrase:
            data.__dict__["niceStr"] = phrase
        else:
            data.__dict__["niceStr"] = self.data["niceStr"]
            logging.debug("Failed to create NL description", extra={
                "type": logging_types.W_TEMPLATE_NOT_FOUND,
                "phrase": self.data["niceStr"]})


    def ParseBool(self, phrase, value):
        """ Bool 1 is positive, Bool 0 negative (sth does not happen) """
        exceptions = ["be", "can", "will", "must"]
        if value:
            phrase_bool = phrase
        elif not value:
            verb = self.finetune.find_verb(self.lang, phrase)
            if verb:
                if self.lang == "cs":
                    phrase_bool = re.sub(verb[0], "".join(["ne", verb[0]]), phrase)
                elif self.lang == "en":
                    verb_lemma = self.finetune.lemmatize(self.lang, verb[0])
                    if verb_lemma in exceptions:
                        phrase_bool = re.sub(r'\b{}\b'.format(verb[0]),  " ".join([verb_lemma, "not"]), phrase)
                    else:
                        phrase_bool = re.sub(r'\b{}\b'.format(verb[0]), " ".join(["does not", verb_lemma]), phrase)
            else:
                phrase_bool = phrase
        return phrase_bool

    def ParseForce(self, phrase, value):
        if value:
            if self.lang == "en":
                phrase = " ".join(["force", phrase])
            elif self.lang == "cs":
                phrase = " ".join(["Vynuť", phrase])
        elif not value:
            phrase = phrase
        return phrase

    def convert_to_dic(self, lists):
        data = lists.__dict__
        return data

    def strip_extra_spaces(self, text):
        stripped_spaces = re.sub(' +', ' ', text)
        stripped_text = stripped_spaces.strip()
        return stripped_text

    def start_stop(self, phrase, state):
        state = self.finetune.conjugate(self.lang, state.lower(), 3)
        verb = self.finetune.find_verb(self.lang, phrase)
        verb_new = verb[0]
        if verb:
            if self.lang == "cs":
                verb_new = self.finetune.lemmatize(self.lang, verb[0])
            elif self.lang == "en":
                verb_new = conjugate(verb[0], tense=PARTICIPLE, parse=True)
            phrase = re.sub(verb[0], " ".join([state, verb_new]), phrase)
            return phrase
        else:
            return phrase

    def MatchAction(self, actor, prog):
        """ Load robot actions and return sring for given program number """
        actor = actor.lower()
        if self.lang == "en":
            with open(EN_PROGRAM_DICT_DIR, 'r', encoding="utf-8") as stream:
                action_list = json.load(stream)
                if actor in action_list:
                    if str(prog) in action_list[actor]:
                        action = action_list[actor][str(prog)]
                    else:
                        action = "execute program {}".format(prog)
                        logging.warning("Warning: Did not find program {} for robot {} in English", prog, actor,
                        extra={"type": logging_types.W_TEMPLATE_NOT_FOUND})
                else:
                    return False

        elif self.lang == "cs":
            with open(CZ_PROGRAM_DICT_DIR, 'r', encoding="utf-8") as stream:
                action_list = json.load(stream)
                if actor in action_list:
                    if str(prog) in action_list[actor]:
                        action = action_list[actor][str(prog)]
                    else:
                        action = "vykonat program {}".format(prog)
                        logging.warning("Warning: Did not find program {} for robot {} in Czech", prog, actor,
                        extra={"type": logging_types.W_TEMPLATE_NOT_FOUND})
                else:
                    return False
        return action

    def MatchGeneral(self, word):
        """ Return nice string for basic form of a word """
        order = 0
        if "_2" in word:
            order = 1
            word = word.split("_")[0]
        with open(GENERAL_YAML_DIR, 'r', encoding="utf-8") as stream:
            phrase_list = yaml.full_load(stream)
        if self.lang in phrase_list and word.lower() in phrase_list[self.lang]:
            phrase = phrase_list[self.lang][word.lower()]
            if type(phrase) is list:
                phrase = phrase[order]
        else:
            phrase = word
        return phrase


