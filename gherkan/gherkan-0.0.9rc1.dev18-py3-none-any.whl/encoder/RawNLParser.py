import os, json, string
import en_coref_md
from pattern.en import parsetree, conjugate, lemma
import re
import gherkan.utils.constants as c
import gherkan.utils.gherkin_keywords as g
from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.encoder.NL2Temp import NLTempMatcher
from gherkan.utils.word_morpho import Finetuner
from gherkan.utils import logging_types
import logging


class RawNLParser:
    def __init__(self, nmm : NLPModelManager = None, feature=None, language="en", splitter="scenario"):
        """
        This class takes the raw text input and outputs the filled gherkin template in NL. It also updates
        the RobotPrograms.json with detected actions of selected subject
        :param feature: the actor we are talking about in the scenarios, i.e. robot R3
                (is filled when there is only "robot" without specification)
        :param language: language of the NL text (en/cs)
        :param subj_of_interest: subject of whom we collect actions and save them to RobotPrograms.json
        :param splitter: word which separates scenarios in NL text
        """
        self.lang = language
        self.split_word = splitter
        self.subj_of_interest = c.SUBJ_OF_INTEREST
        self.actor_uni = feature
        self.cleaner = NLTempMatcher(lang=self.lang, nmm=nmm, feature=feature)
        self.finetune = Finetuner(self.lang, nmm)
        self.text_raw = None
        self.robot_actions = []
        self.text_lines_normalized = []
        self.sentences = []
        self.keywords = [g.GIVEN, g.WHEN, g.THEN]
        if self.lang == "cs":
            self.keywords = [g.GIVEN_CS, g.WHEN_CS, g.THEN_CS]

    def parse(self, text_raw: str, background=False):
        """The main parser outputting the Given. When, Then template"""
        self.text_raw = text_raw
        scenarios = self.separate_scenarios(text_raw, self.split_word)
        for scenario in scenarios:
            logging.info("Processing scenario: {}", scenario)
            scenario = self.strip_extra_spaces(scenario)
            if not background:
              self.text_lines_normalized.append("Scenario: {}".format(scenario))
            text = self.replace_synonyms(scenario)
            self.find_patterns(text)
            phrases = self.prune_keywords(self.sentences)
            for phrase in phrases:
                    phrase = self.substitute_feature(phrase)
                    self.collect_subject_actions(phrase)
            for sentence in self.sentences:
                clean = self.strip_extra_spaces(sentence)
                if not background:
                   self.text_lines_normalized.append(clean)
                else:
                    return clean
            self.sentences = []

        logging.info("Detected actions connected with {}s: {}", self.subj_of_interest, self.robot_actions)

    def prune_keywords(self, text):
        """Separate sentences with AND/OR and also leave out keywords"""
        separators = {"en":["OR", "AND"], "cs":["NEBO", "A"]}
        pruned = []

        for phrase in text:
            sent = re.sub(r'\b({}|{}|{})\b'.format(*self.keywords), "", phrase, re.IGNORECASE)
            for x in separators[self.lang]:
                if isinstance(sent, list):
                    for y in sent:
                        sent_y = list(filter(None, re.split(r'\b{}\b'.format(x), y)))
                        sent_y = [x for x in sent_y if x.lower() != []]
                        pruned.extend(sent_y)
                else:
                    sent = list(filter(None, re.split(x, sent)))
                    sent = [x for x in sent if x.lower() != []]
        return pruned

    def get_text_lines(self):
        return self.text_lines_normalized

    def substitute_feature(self, phrase):
        """If there is no specification of the subject, we take it from the feature (e.g. robot > robot R1)"""
        actor = re.findall(r'{}\s+([A-Za-z0-9]{})\b'.format(self.subj_of_interest,"{1,3}"), phrase, re.IGNORECASE)
        if not actor:
            if self.subj_of_interest in self.actor_uni.lower():
               try:
                    actor_uni = " ".join([self.actor_uni.split()[0].lower(), self.actor_uni.split()[1].upper()])
               except:
                    actor_uni = self.actor_uni
            else:
                return phrase
            actor_new = actor_uni
            phrase = re.sub(r"\b{}\b".format(self.subj_of_interest), actor_new, phrase, re.IGNORECASE)
        return phrase

    def fix_word_order(self, text):
        """In Czech, change word order if verb is before subject"""
        phrase = re.sub(r'\b{}|{}\s'.format("Vynuť", "Uvolni"), "", text, re.IGNORECASE)
        w_order = ""
        new_v_pos = None
        for word in phrase.split():
            if word.isupper():
                w_order += "C"
            else:
                word_info = self.finetune.get_txt_info(word)
                w_order += (word_info[0]["pos"])
        if w_order[1] == "V":   # if verb is after keyword
            for idx, letter in enumerate(w_order[2:]):
                if letter != "N" and letter != "C":   # find first word which is not noun or number
                    if new_v_pos is None:
                        new_v_pos = idx + 2
                        if phrase is not text:
                            phrase = text
                            new_v_pos = new_v_pos + 1
                        new_phrase = phrase.split()
                        new_phrase.insert(new_v_pos, phrase.split()[1])
                        del new_phrase[1]
                        phrase = " ".join(new_phrase)
        else:
            phrase = text
        return phrase

    def replace_synonyms(self, command):
        """place words in command with synonyms defined in synonym_file"""
        synonyms_filename = os.path.join(
            c.GHERKAN_ROOT_DIR, "utils", "synonyms.json")
        with open(synonyms_filename, encoding="utf-8") as f:
            synonyms = json.load(f)
        for key in synonyms[self.lang]:
            for phrase in synonyms[self.lang][key]:
                if phrase in command.lower():
                    src_str = re.compile(r'\b{}\b'.format(phrase), re.IGNORECASE)
                    command = src_str.sub(key, command)
        command = self.strip_extra_spaces(re.sub(r"\stodelete", "", command))
        number_words = re.findall(r'\b({}|{})\b\s*[0-9]'.format("číslo", "number"), command, re.IGNORECASE)
        for x in number_words:
            command = re.sub(r'\b{}\b'.format(x), "", command, re.IGNORECASE)
        return command

    def find_patterns(self, text):
        """ Detects sentences framed with template keywords. Sentences without any keyword are detected as Then.
        CONDITION: if there is no "then", there must be at least a comma to separate the sentence"""
        for keyword in self.keywords:
            text = re.sub(r'\b{}\b'.format(keyword.lower()), keyword, text, re.MULTILINE)
        split = re.findall(
            r'\b(?:{0}|{1}|{2})\b.+?(?={0}|{1}|{2}|$)'.format(*self.keywords), text, re.IGNORECASE | re.MULTILINE)
        rest = None
        if len(split) >= 1:
           rest = list(filter(None, re.split(r'\.|,', split[-1], re.IGNORECASE)))
        try:
            if rest:
                for idx, x in enumerate(rest):
                    keyword = re.findall(r'\b{0}|{1}|{2}\b'.format(*self.keywords), x, re.IGNORECASE)
                    if not keyword:
                        rest[idx] = " ".join([self.keywords[2], x])
                split = split[:-1] + rest
        except:
            pass
        temp_dic = {"en": [["AND", "OR", "BUT"], ["and", "or", "but"]],
                    "cs": [["A", "NEBO", "ALE"], ["a", "nebo", "ale"]]}
        for x in split:
            phrase = x.translate(str.maketrans('', '', string.punctuation))
            phrase = self.strip_extra_spaces(phrase)
            for idx, keyword in enumerate(temp_dic[self.lang][0]):
                for x in range(1,4):
                    phrase = re.sub(r'\b{}\b'.format(temp_dic[self.lang][1][idx]), "".join([" ", keyword, " "]), phrase,re.IGNORECASE) # for some reason it sometimes misses some words on first try
            if self.lang == "cs":
                phrase = self.fix_word_order(phrase)
            self.sentences.append(phrase)
        self.sentences = list(set(self.sentences))
        corr_order = [[], [], []]  # Reorder list to Given,When,Then
        for idx, x in enumerate(self.keywords):
            for i in self.sentences:
                if x.lower() in i.lower():
                    i = re.sub(x.lower(), x, i)
                    corr_order[idx] = i
        self.sentences = list(filter(None, corr_order))
        return self.sentences

    def check_if_unique(self, program_dict, actor, action_lemma):
        default_verbs = ["začít", "skončit", "zastavit", "start", "stop", "end"]
        if actor in program_dict.keys():
            is_unique = True
            # find if the action is already in list
            for key in program_dict[actor]:
                if self.strip_extra_spaces(action_lemma) == program_dict[actor][key]:
                    is_unique = False
            if is_unique:
                if "program" in action_lemma.split()[-1] or action_lemma.split()[-1] in default_verbs:
                  pass
                else:
                    new_key = len(program_dict[actor]) + 1
                    program_dict[actor].update(
                        {new_key: self.strip_extra_spaces(action_lemma.lower())})
        else:
            if "program" in action_lemma.split()[-1] or action_lemma.split()[-1] in default_verbs:
                pass
            program_dict[actor] = {1: self.strip_extra_spaces(action_lemma)}
        return program_dict

    def generate_program_dict(self, make_new=True):
        """ make_new - creates a new dict and replaces old one. If False, programs are appended to current dict """
        program_dict = {}
        dict_path = os.path.join(c.GHERKAN_ROOT_DIR, "utils", "".join(["RobotPrograms_", self.lang, ".json"]))
        if not make_new:
            with open(dict_path, 'r', encoding="utf-8") as f:
                program_dict = json.load(f)
                f.close()
        if self.robot_actions:
            if self.lang == "en":
                for action in self.robot_actions:
                    actor_new = re.findall(r'({}\s+([a-z]+)*([0-9])*([a-z]+)*)'.format(self.subj_of_interest), action, re.IGNORECASE)
                    try:
                        actor = actor_new[0][0]
                    except:
                        pass
                    if not actor:  # if no specification, use the one defined in Feature
                        actor = self.actor_uni.lower()
                        action = re.sub("{}".format(self.subj_of_interest), "", action, re.IGNORECASE)
                    action_lemma = self.finetune.lemmatize_sentence(self.lang, "".join(action.lower().rsplit(actor.lower())))
                    program_dict = self.check_if_unique(program_dict, actor.lower(), action_lemma)
            elif self.lang == "cs":
                for action in self.robot_actions:
                    actor = re.findall(r'({}\s+(([a-z]+)*([0-9])*|([0-9])*([a-z]+)*))\s'.format(self.subj_of_interest), action, re.IGNORECASE)
                    if not actor:
                        actor = self.subj_of_interest
                        try:
                           actor_uni = " ".join([self.actor_uni.split()[0].lower(), self.actor_uni.split()[1].upper()])
                        except:
                            actor_uni = self.actor_uni
                        actor_new = actor_uni
                    else:
                        actor = actor[0][0]
                        actor_new = actor
                    action = self.cleaner.lemmatize(action)
                    action_lemma = re.sub(r'\b{}\b'.format(actor), "", action, re.IGNORECASE)
                    action_lemma = self.finetune.lemmatize_sentence(self.lang, action_lemma)
                    program_dict = self.check_if_unique(program_dict, actor_new.lower(), action_lemma)
            with open(dict_path, 'w', encoding="utf-8") as f:
                json.dump(program_dict, f, ensure_ascii=False, indent=4)
            logging.info("Updated program list: {}", program_dict)

    def strip_extra_spaces(self, text):
        stripped_spaces = re.sub(' +', ' ', text)
        stripped_text = stripped_spaces.strip()
        return stripped_text

    def collect_subject_actions(self, text):
        """ Detect any actions performed by subject of interest"""
        if self.lang == "en":
            tree = parsetree(text, tokenize=True, tags=True,
                             chunks=True, relations=True)
            for x in tree:  # now we select sentences with robot subjects or passive form
                for chunk in x.chunks:
                    if x.subjects:
                        if chunk.string in x.subjects[0].string:
                            if self.subj_of_interest.lower() in chunk.string.lower():  # active verb form
                                bool = self.cleaner.get_negative(x.string)
                                force, unforce = self.cleaner.get_force_unforce(x.string)
                                state, phrase = self.cleaner.get_state(x.string)
                                sentence_new = self.cleaner.get_cleanphr(phrase, bool, force, unforce)
                                self.robot_actions.append(sentence_new)
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
                            rest = re.sub(r"\b{}\b".format(chunk.string), "", verb_object, re.IGNORECASE)
                    sent = subject + " " + ' '.join(verbs) + " " + rest
                    # sent = sent.translate(
                    #     str.maketrans('', '', string.punctuation))
                    bool = self.cleaner.get_negative(sent)
                    force, unforce = self.cleaner.get_force_unforce(sent)
                    sentence_new = self.cleaner.get_cleanphr(sent, bool, force, unforce)
                    self.robot_actions.append(sentence_new)

        elif self.lang == "cs":
            if self.subj_of_interest in text.split():
                bool = self.cleaner.get_negative(text)
                force, unforce = self.cleaner.get_force_unforce(text)
                state, phrase = self.cleaner.get_state(text)
                sentence_new = self.cleaner.get_cleanphr(phrase, bool, force, unforce)
                verb = self.finetune.find_verb(self.lang, sentence_new)
                if verb:
                    verb_lemma = self.finetune.lemmatize(self.lang, verb[0])
                    sentence_new = re.sub(verb[0], verb_lemma, sentence_new)
                self.robot_actions.append(sentence_new)
        # now remove duplicit actions:
        self.robot_actions = list(set(self.robot_actions))

    def solve_corefs(self, text):
        print("Loading Neuralcoref module...")
        nlc = en_coref_md.load()
        dok = nlc(text)
        if dok._.has_coref == 1:
            replaced_corefs = dok._.coref_resolved
        else:
            replaced_corefs = text
        print("Done")
        # print("Corref: " + replaced_corefs)

        return replaced_corefs

    def separate_scenarios(self, text, split_word):
        """Returns a list of scenarios separated by self.split_word. Upper case does not matter"""
        splitter = re.compile(r'\s*({})\s*'.format(split_word), re.IGNORECASE)
        split = re.split(splitter, text)
        split = list(filter(None, split))
        split_cl = [x for x in split if x.lower() != split_word]
        return split_cl

    def replace(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))

        return regex.sub(lambda match: substitutions[match.group(0)], string)
