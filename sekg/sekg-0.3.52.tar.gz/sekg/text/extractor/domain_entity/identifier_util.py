import re

import spacy
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet as wn, stopwords

from sekg.text.extractor.domain_entity.relation_detection import RelationType
from sekg.util.code import CodeElementNameUtil


class IdentifierHelper:
    # SPECIAL_VERB = {"get", "set", "parse", "push", "pop", "peak", "load", "flush", "init", "goto", "show", "finish",
    #                 "invoke",
    #                 "update", "open", "close", "import", "move", "post", "process", "lookup", "select", "clear",
    #                 "reload", "prepend", "print", "claim", "visit", "resize", "build", "convert"}
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

    @staticmethod
    def couldBeVerb(word):
        """
        check if a word could be a verb
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            if name == word:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "v" in tag_count:
            return True
        return False

    @staticmethod
    def couldBeNoun(word):
        """
        check if a verb could be noun
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            if name == word:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "n" in tag_count:
            return True
        return False

    def uncamelize(self, camel_case):
        if camel_case in self.camel_cache:
            return self.camel_cache[camel_case]
        sub = self.CODE_NAME_UTIL.uncamelize_by_stemming(camel_case)
        self.camel_cache[camel_case] = sub
        return sub

    @staticmethod
    def couldBeADJ(word):
        """
        check if a word could be adj
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            if name == word:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "a" in tag_count:
            return True
        return False

    def pos_tag_for_method_name(self, name):
        """
        do the pos tag for method name
        :param name: name
        :return: a Spacy Doc object
        """
        name = name.split("(")[0].split(".")[-1]
        uncamel = self.uncamelize(name).lower()
        spacy_doc = self.nlp(uncamel)

        # fix the problem of 2 and 4 to represent 'to' and 'for'
        for i in range(0, len(spacy_doc)):
            if spacy_doc[i].text == "2" and i != 0 and len(spacy_doc) - 1:
                spacy_doc[i].lemma_ = "to"
                spacy_doc[i].pos_ = "ADP"
                spacy_doc[i].tag_ = "IN"

            if spacy_doc[i].text == "4" and i != 0 and len(spacy_doc) - 1:
                spacy_doc[i].lemma_ = "for"
                spacy_doc[i].pos_ = "ADP"
                spacy_doc[i].tag_ = "IN"

            if spacy_doc[i].text.lower() == "to":
                spacy_doc[i].lemma_ = "to"
                spacy_doc[i].pos_ = "ADP"
                spacy_doc[i].tag_ = "IN"

            if spacy_doc[i].text.lower() in ["id", "ID", "Id"]:
                spacy_doc[i].lemma_ = "id"
                spacy_doc[i].pos_ = "NOUN"
                spacy_doc[i].tag_ = "NN"

        parts = []
        current_part = []
        for token in spacy_doc:
            if token.pos_ == "ADP":
                if current_part:
                    parts.append(current_part)
                current_part = []
                parts.append([token])
            else:
                current_part.append(token)
        if current_part:
            parts.append(current_part)

        if len(parts) == 3 and parts[1][0].text == "2":
            self.reannotation_for_tokens(parts[0], fix_to_noun_ending=True)
            self.reannotation_for_tokens(parts[2], fix_to_noun_ending=True)
            return spacy_doc

        leading_tokens = parts[0]
        self.reannotate_for_leading_part_tokens(leading_tokens)

        left_parts = parts[1:]
        if len(left_parts) == 0:
            return spacy_doc

        for tokens in left_parts:
            # 介词后面的作为独立的一部分，让spacy重新标注
            if len(tokens) == 1 and tokens[0].pos_ == "ADP":
                continue

            self.reannotate_for_left_part_tokens_after_preposition(tokens)
        return spacy_doc

    def reannotate_for_leading_part_tokens(self, part):
        text = " ".join([token.text for token in part])
        # for "find or create" type, just use the default annotation, it is OK
        if "and" in text.lower() or "or" in text.lower():
            self.reannotation_for_tokens(part)
            return
            # todo
        if len(part) == 1:
            # first part is a ADP(eg. To,By)
            if part[0].pos_ == "ADP":
                return
            # new_token = self.nlp(part[0].text)[0]
            # self.update_annotation_for_token(part[0],new_token)
            if self.couldBeVerb(part[0].text):
                self.set_token_to_verb_pos(part[0])
                return
            if self.couldBeNoun(part[0].text):
                self.set_token_to_noun_pos(part[0])
                return
            if self.couldBeADJ(part[0].text):
                self.set_token_to_adj_pos(part[0])
                return
            return

        if len(part) >= 1:
            ## 1. VERB + NOUN
            ## 2. VERB + NOUN +ADJ
            ## 3. VERB + ADJ
            ## 4. NOUN

            left_tokens = part
            if self.couldBeVerb(part[0].text):
                self.set_token_to_verb_pos(part[0])
                left_tokens = part[1:]

            if self.couldBeNoun(left_tokens[-1].text):
                print(" couldBeNoun ", left_tokens[-1].text)

                ## 1. VERB + NOUN
                ## 4. NOUN
                self.reannotation_for_tokens(left_tokens, fix_to_noun_ending=True)
                return

            if self.couldBeADJ(left_tokens[-1].text):
                print("couldbe ADJ ", left_tokens[-1].text)
                ## 2. VERB + NOUN +ADJ
                ## 3. VERB + ADJ
                self.set_token_to_adj_pos(left_tokens[-1])
                left_tokens = left_tokens[:-1]
                self.reannotation_for_tokens(left_tokens, fix_to_noun_ending=True)
                return

            self.reannotation_for_tokens(left_tokens)

    def reannotate_for_left_part_tokens_after_preposition(self, tokens):
        text = " ".join([token.text for token in tokens])
        # for "find or create" type, just use the default annotation, it is OK
        if "and" in text.lower() or "or" in text.lower():
            self.reannotation_for_tokens(tokens)
            return
        if len(tokens) == 1:
            # ADP+NOUN
            if self.couldBeNoun(tokens[0].text):
                self.set_token_to_noun_pos(tokens[0])
                return
            # ADP+ADJ
            if self.couldBeADJ(tokens[0].text):
                self.set_token_to_adj_pos(tokens[0])
                return
            # others: annotate by default
            self.reannotation_for_tokens(tokens)
            return

        if len(tokens) >= 1:
            ## 1. NOUN
            ## 2. NOUN +ADJ
            ## 3. ADJ
            ## 4. NOUN

            if self.couldBeNoun(tokens[-1].text):
                ## 1. NOUN
                ## 4. NOUN
                self.reannotation_for_tokens(tokens, fix_to_noun_ending=True)
                return

            if self.couldBeADJ(tokens[-1].text):
                ## 2. VERB + NOUN +ADJ
                ## 3. VERB + ADJ
                self.set_token_to_adj_pos(tokens[-1])

                self.reannotation_for_tokens(tokens[:-1], fix_to_noun_ending=True)
                return

            self.reannotation_for_tokens(tokens)

    def reannotation_for_tokens(self, tokens, fix_to_noun_ending=False):
        if len(tokens) == 0:
            return
        text = " ".join([token.text for token in tokens])
        new_tokens = self.nlp(text)
        if len(new_tokens) != len(tokens):
            print("error when retokenize the len is not the same")
            for token in tokens:
                new_token = self.nlp(token.text)[0]
                self.update_annotation_for_token(token, new_token)
        else:
            for old_annotation_token, new_annotation_token in zip(tokens, new_tokens):
                self.update_annotation_for_token(old_annotation_token, new_annotation_token)

        self.fix_adj_like_verb_annotation(tokens)
        self.fix_special_vocab_annotation(tokens)
        if fix_to_noun_ending and self.couldBeNoun(tokens[-1].text):
            self.set_token_to_noun_pos(tokens[-1])

    def fix_adj_like_verb_annotation(self, tokens):
        for token in tokens:
            if token.tag_ in ["VBD", "VBG", "VBN"]:
                self.set_token_to_adj_pos(token)

    def fix_special_vocab_annotation(self, tokens):
        for token in tokens:
            if token.text.lower() == "id":
                token.lemma_ = "id"
                token.pos_ = "NOUN"
                token.tag_ = "NN"

    def update_annotation_for_token(self, old_annotation_token, new_annotation_token):
        old_annotation_token.lemma_ = new_annotation_token.lemma_
        old_annotation_token.pos_ = new_annotation_token.pos_
        old_annotation_token.tag_ = new_annotation_token.tag_

    def set_token_to_verb_pos(self, old_annotation_token):
        # old_annotation_token.lemma_ = new_annotation_token.lemma_
        old_annotation_token.pos_ = "VERB"
        old_annotation_token.tag_ = "VB"

    def set_token_to_noun_pos(self, old_annotation_token):
        # old_annotation_token.lemma_ = new_annotation_token.lemma_
        old_annotation_token.pos_ = "NOUN"
        old_annotation_token.tag_ = "NN"

    def set_token_to_adj_pos(self, old_annotation_token):
        # old_annotation_token.lemma_ = new_annotation_token.lemma_
        old_annotation_token.pos_ = "ADJ"
        old_annotation_token.tag_ = "JJ"

    def find_depending_verbs(self, np_tokens, spacy_doc):
        spacy_doc = [token for token in spacy_doc]
        result = []
        start_token = np_tokens[0]
        start_index = spacy_doc.index(start_token)
        print("----start_token", start_token, start_token)

        for i in range(start_index - 1, -1, -1):
            print("----try find verb for relation", spacy_doc[i])

            if spacy_doc[i].pos_ == "VERB":
                result.append(spacy_doc[i])
                print("find verb for relation", spacy_doc[i])
                if i - 2 < 0:
                    return result

                if spacy_doc[i - 1].text.lower() != "and" and spacy_doc[i - 1].text.lower() != "or":
                    return result

                if spacy_doc[i - 2].pos_ != "VERB":
                    return result
                result.append(spacy_doc[i - 2])
                return result

        return result

    def find_adp_token_between_verb_and_np(self, spacy_doc, np_tokens, operation_token):
        spacy_doc = [token for token in spacy_doc]

        operation_token_index = spacy_doc.index(operation_token)
        start_token = np_tokens[0]
        start_index = spacy_doc.index(start_token)

        for i in range(start_index - 1, operation_token_index, -1):
            if spacy_doc[i].pos_ == "ADP":
                return spacy_doc[i]
        return None

    def reextract_np_from_single_part(self, tokens):
        if len(tokens) == 0:
            return []

        text = " ".join([token.text for token in tokens]).lower()

        text = " ".join([token.text + "" + token.pos_ for token in tokens]).lower()
        print(text)
        total_nps = []
        current_np = []

        for index, token in enumerate(tokens):
            if token.pos_ == "ADP" and token.text.lower() == "of":
                if len(current_np) == 0:
                    current_np = []
                    continue

                if current_np[-1].pos_ not in ["PROPN", "NOUN"]:
                    current_np = []
                    continue

                current_np.append(token)
                continue
            if token.tag_ in ["WP$", "WDT", "WP"] or token.pos_ not in ["CCONJ", "ADJ", "PROPN", "NOUN"]:
                if len(current_np) == 0:
                    continue
                if current_np[-1].pos_ not in ["PROPN", "NOUN"]:
                    current_np = []
                    continue

                total_nps.append(current_np)
                current_np = []
                continue
            current_np.append(token)
            continue

        if len(current_np) != 0 and current_np[-1].pos_ in ["PROPN", "NOUN"]:
            total_nps.append(current_np)

        if len(total_nps) == 0:
            return []
        if len(total_nps) == 1:
            return total_nps

        return total_nps

    def reextract_np_from_spacy_pos_doc(self, tokens):
        if len(tokens) == 0:
            return []

        parts = []
        current_part = []
        for token in tokens:
            if token.pos_ == "ADP" and token.text.lower() != "of":
                if current_part:
                    parts.append(current_part)
                current_part = []
            else:
                current_part.append(token)
        if current_part:
            parts.append(current_part)
        noun_phase_list = []

        for part in parts:
            print(noun_phase_list, "----")

            nps = self.reextract_np_from_single_part(part)
            if len(nps) > 0:
                noun_phase_list.extend(nps)
        print(noun_phase_list, "----")
        return noun_phase_list

    def extract_from_method_name_lmw_version(self, method_name):
        terms = set()
        operations = set()

        spacy_doc = self.pos_tag_for_method_name(method_name)
        noun_chunks = self.reextract_np_from_spacy_pos_doc(spacy_doc)

        operations.update([token.text for token in spacy_doc if token.pos_ == "VERB"])
        terms.update([" ".join([t.text for t in np_tokens]).lower() for np_tokens in noun_chunks])

        text = " ".join([token.text for token in spacy_doc]).lower()

        # group the operation by level, eg. "create and find", "create" and "find" are the same level.

        operation_2_np_relations = set([])
        method_2_np_relations = set([])

        for np_tokens in noun_chunks:
            print("when find relation", np_tokens)
            np = " ".join([t.text for t in np_tokens]).lower()
            operation_tokens = self.find_depending_verbs(np_tokens, spacy_doc)
            print("when find relation np", np_tokens)
            print("when find relation operation_tokens", operation_tokens)

            for operation_token in operation_tokens:
                operation_2_np_relations.add((np, RelationType.CAN_BE_OPERATED.value, operation_token.lemma_.lower()))

            for operation_token in operation_tokens:
                adp_token = self.find_adp_token_between_verb_and_np(spacy_doc, np_tokens, operation_token)
                adp_text = ""
                if adp_token == None:
                    adp_text = ""
                else:
                    adp_text = adp_token.text

                operation_2_np_relations.add((np, RelationType.CAN_BE_OPERATED.value, operation_token.lemma_.lower()))

                operation_relation_name = ("operation_" + operation_token.lemma_.lower() + " " + adp_text).strip()
                method_2_np_relations.add((method_name, operation_relation_name, np))

        return terms, operations, operation_2_np_relations, method_2_np_relations

    def extract_from_variable(self, variable):
        """
        extract from variable name , eg. "String filePath"
        :param variable: s string that represent variable , eg. "String filePath", "java.lang.String filePath"
        :return:
        """
        terms = set()
        variable = variable.split("<")[0].split(".")[-1].split(" ")[-1]
        if not variable:
            return set(), set()
        uncamel = self.uncamelize(variable)
        for np in self.nlp(uncamel).noun_chunks:
            lemma = " ".join([token.lemma_ for token in np if token.lemma_ != "-PRON-"])
            if len(lemma) < 1 or lemma.isdigit() == True:
                continue

            terms.add(lemma)
        return terms

    def extract_from_class_name(self, name):
        """
        extract from class name or the name like class. eg. package name. example: java.lang.ArrayList-> Array List
        :param name:
        :return:
        """
        # todo: Error raise: IndexError: list index out of range
        name = name.split("<")[0].split(".")[-1].split(" ")[-1]
        if not name:
            return set()
        uncamel = self.uncamelize(name)
        lemma = " ".join([token.lemma_ for token in self.nlp(uncamel) if token.lemma_ != "-PRON-"])
        return {lemma}

    # following is the version of wc to implement to extract relation from method name
    # def extract_from_method_name_wc_version(self, name):
    #     terms = set()
    #     operations = set()
    #     name = name.split("(")[0].split(".")[-1]
    #     uncamel = self.uncamelize(name).lower()
    #     words = uncamel.split()
    #     print("words", words)
    #
    #     spacy_doc = self.nlp(uncamel)
    #
    #     pos_tags = [token.pos_ for token in spacy_doc]
    #     lemma_words = [token.lemma_ for token in spacy_doc]
    #     np_index = {np.start: np.end for np in spacy_doc.noun_chunks}
    #     print("before fix the tags and lemma", pos_tags, lemma_words)
    #
    #     if len(words) == 1:
    #         if pos_tags[0] == "VERB":
    #             return set(), {words[0]}
    #         if pos_tags[0] == "NOUN":
    #             return {words[0]}, set()
    #
    #         return terms, {words[0]}
    #
    #     parts = []
    #     index = 0
    #     word_num = len(lemma_words)
    #     adj_flag = -1
    #     while index < word_num:
    #         if index in np_index:
    #             np_words = lemma_words[index: np_index[index]]
    #             if np_words[0] in self.SPECIAL_VERB:
    #                 parts.append((np_words[0], "VERB"))
    #                 np = " ".join(np_words[1:])
    #             else:
    #                 np = " ".join(np_words)
    #             if len(np) > 0:
    #                 if adj_flag >= 0:
    #                     np = lemma_words[adj_flag] + " " + np
    #                 parts.append((np, "NP"))
    #             index = np_index[index]
    #             adj_flag = -1
    #         elif lemma_words[index] in {"id", "ID", "Id"}:
    #             np = lemma_words[index]
    #             if adj_flag >= 0:
    #                 np = lemma_words[adj_flag] + " " + np
    #
    #             elif len(parts) > 0 and parts[-1][1] == "NP":
    #                 ele, tag = parts.pop()
    #                 np = "{} {}".format(ele, lemma_words[index])
    #             parts.append((np, "NP"))
    #             index += 1
    #             adj_flag = -1
    #         elif pos_tags[index] == "VERB" and lemma_words[index].endswith("ed"):
    #             adj_flag = index
    #             index += 1
    #         else:
    #             adj_flag = -1
    #             parts.append((lemma_words[index], pos_tags[index]))
    #             index += 1
    #     index = 0
    #     np_flag = -1
    #     of_flag = -1
    #     while index < len(parts):
    #         ele, tag = parts[index]
    #         if tag == "NP":
    #             if of_flag >= 0:
    #                 cur = parts.pop(index)[0]
    #                 of = parts.pop(index - 1)[0]
    #                 prev = parts.pop(index - 2)[0]
    #                 np = " ".join([prev, of, cur])
    #                 parts.append((np, "NP"))
    #                 index = index - 2
    #                 of_flag = -1
    #             else:
    #                 np_flag = index
    #                 index += 1
    #         elif ele == "of" and of_flag < 0 and np_flag >= 0:
    #             of_flag = index
    #             index += 1
    #         else:
    #             np_flag = -1
    #             of_flag = -1
    #             index += 1
    #     # print(parts)
    #     operations.update([ele for ele, tag in parts if tag == "VERB"])
    #     nps = {ele for ele, tag in parts if tag == "NP"}
    #     terms.update(nps)
    #     print("pos tags", parts)
    #
    #     return terms, operations
