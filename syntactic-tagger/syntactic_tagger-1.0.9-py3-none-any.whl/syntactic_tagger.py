#!/usr/bin/env python
u"""Provides de class SyntacticTagger, which is a part-of-speech tagger and lemmatizer for Spanish.
"""

import msgpacku as msgpack
import bz2
from itertools import chain, product
from os.path import dirname, realpath, join, getsize
from math import log10
from re import sub
from iar_tokenizer import Tokenizer

# Constants
NOUN = "N"
COMMON = "C"
PROPER = "P"
MASCULINE = "M"
FEMININE = "F"
SINGULAR = "S"
PLURAL = "P"
INVARIABLE = "I"
ADJECTIVE = "A"
DETERMINER = "D"
PRONOUN = "P"
VERB = "V"
ADVERB = "R"
PREPOSITION = "S"
CONJUNCTION = "C"
INTERJECTION = "I"
PUNCTUATION = "F"
NUMBER = "Z"
AFFIX = "-"
ONOMATOPOEIA = "O"
EXPRESSION = "E"
UNKNOWN = "?"


class SyntacticTagger:
    """This class is a part-of-speech tagger. It uses a lexicon and a syntactic table to choose the tags.

    The main idea is that a lexicon provides the possible tags for each token, and the syntactic table is
    used in order to choose which of those tags is the most "probable" one.
    The syntactic table has been trained used the Spanish Wikipedia, and contains all the possible POS tags
    combinations seen in it with a weighting whose value is based on the frequency of occurrence, the
    information from an electronic dictionary and the overal frequency of occurrence of the different
    syntactic categories in a plain text corpus.
    """

    def __init__(self):
        """Initializes the class by loading the data files needed for the tagging.
        """
        self._syntactic_table = {}
        for order_table in range(6):
            self._syntactic_table.update(self.load_data('syntactic_table' + str(order_table)))
        self._lexicon = self.load_data('lexicon')
        self._tag_number_converter = self.load_data('tag_number_converter')
        self._form_count = self.load_data('form_count')
        self._prefixes = self.load_data('prefixes')

    @staticmethod
    def load_data(data_type):
        """Used in the SyntacticTagger initializer to load a data file.

        :type data_type: str
        :param data_type: The name of the data file to be loaded.
        """
        data_file_path = join(dirname(realpath(__file__)), 'data_files', data_type + '.msgpack')
        if getsize(data_file_path) > 0:
            with open(data_file_path, 'rb') as data_file:
                return msgpack.unpack(data_file, use_list=False, encoding="utf-8")
        else:
            bz2_data_file_path = join(dirname(realpath(__file__)), 'data_files', data_type + '.msgpack.bz2')
            with bz2.BZ2File(bz2_data_file_path, 'rb') as bz2_data_file:
                data = msgpack.unpack(bz2_data_file, use_list=False, encoding="utf-8")
            with open(data_file_path, 'wb') as data_file:
                msgpack.pack(data, data_file)
            open(bz2_data_file_path, 'wb').close()
            return data

    def get_possible_tags(self, token, proper_nouns_are_lemmas=True):
        """

        :type token: str
        :param token: The token whose possible tags are going to be returned.
        :type proper_nouns_are_lemmas: bool
        :param proper_nouns_are_lemmas: If True, proper nouns are considered to be lemmas, so the
        corresponding lemma of a proper noun is the proper noun itself. Otherwise, when lemmatizing something
        such as "Arias", the returned lemma would be "Aria", since the last "s" is considered to be the plural
        mark.
        :rtype: dict
        :return: A dictionary, containing as keys the possible morphosyntactic tags the token could receive,
        and as values, a tuple containing the weighting as it first value and the lemma as the second.
        """
        prefix = ''
        if token not in self._lexicon:
            # As the token does not appear in the lexicon, we will check whether the lowercased token appears
            # or not. In that case, we use it.
            # TODO: This might not make much sense, since words at the beginning of a sentence are already
            #  lowercased if necessary.
            if token.lower() in self._lexicon:
                token = token.lower()
            else:
                # It does not appear in the lexicon in lowercase. We check whether the token contains dashes
                # dividing two words or any other symbol.
                original_token = token
                retokenized_token = Tokenizer.segmenta_por_palabras(
                        Tokenizer.segmenta_por_frases(token, elimina_separadores=True,
                                                      elimina_separadores_blancos=True,
                                                      incluye_parentesis=True,
                                                      adjunta_separadores=False, agrupa_separadores=False),
                        elimina_separadores=True, segmenta_por_guiones_internos=True,
                        segmenta_por_guiones_externos=True, segmenta_por_apostrofos_internos=False,
                        segmenta_por_apostrofos_externos=True, adjunta_separadores=False,
                        agrupa_separadores=False)[-1]
                if retokenized_token in self._lexicon:
                    prefix = token[:-len(retokenized_token)]
                    token = retokenized_token
                elif retokenized_token.lower() in self._lexicon:
                    prefix = token[:-len(retokenized_token)]
                    token = retokenized_token.lower()
                else:
                    # Otherwise, we try to find a prefix at the beginning of the token.
                    unprefixed_token = self.get_unprefixed_form(retokenized_token.lower())
                    if unprefixed_token != token.lower():
                        prefix = token[:len(token) - len(unprefixed_token)].lower()
                        token = unprefixed_token
                # In case we have modified the original token, we verify that the resulting token is not any
                # other thing but a noun, and adjective or a verb.
                if token in self._lexicon:
                    if len([tag for lemma, weighted_tags in self._lexicon[token].items()
                            for tag in weighted_tags.keys()
                            if self._tag_number_converter[tag][0] not in NOUN + ADJECTIVE + VERB]):
                        token = original_token
                        prefix = ''

        if token in self._lexicon:
            token_tags = {}
            for lemma, weighted_tags in self._lexicon[token].items():
                for tag, weighting in weighted_tags.items():
                    # There is the possibility that the token gets the same tag coming from different lemmas.
                    # In that case, we add the weighting.
                    token_tags[tag] = token_tags.setdefault(tag, [0.0, (weighting, lemma)])
                    token_tags[tag][0] += weighting
                    if lemma != token_tags[tag][1][1]:
                        # Adverbs ending in "-mente" are lemmatized as the adjective from which they
                        # derive.
                        if token_tags[tag][1][0] < weighting or\
                                (token_tags[tag][1][0] == weighting and
                                 len(lemma) < len(token_tags[tag][1][1])):
                            token_tags[tag][1] = (weighting, lemma)
            token_tags = {tag: (value[0], prefix + value[1][1])
                          for tag, value in token_tags.items()}
            return token_tags

        # If we can not find the token in the lexicon, we will tag it as a proper/common noun or a number.
        has_apostrophe = sum(1 if apostrophe in token[1:-1] else 0 for apostrophe in u"'‘`’´") > 0
        if token[0] != token[0].lower() or has_apostrophe:
            if len(token) == 1 or token[1:] == token[1:].lower() or has_apostrophe:
                # There is only a single uppercase character.
                if token[-1] == 's':
                    number = PLURAL
                    gender = FEMININE if len(token) > 1 and token[-2] == 'a'\
                        else MASCULINE if len(token) > 1 and token[-2] == 'o' else COMMON
                    if proper_nouns_are_lemmas:
                        lemma = token
                    else:
                        lemma = token[:-1]
                else:
                    number = SINGULAR
                    gender = FEMININE if token[-1] == 'a' else MASCULINE if token[-1] == 'o' else COMMON
                    lemma = token
                tag = NOUN + PROPER + gender + number
            else:
                # There are more than one uppercase character.
                tag = NOUN + PROPER + COMMON + INVARIABLE
                lemma = token
            token_tags = {self._tag_number_converter[tag]: (1.0, lemma)}
        else:
            if any(char.isdigit() for char in token):
                token_tags = {self._tag_number_converter[NUMBER]: (1.0, token)}
            elif token.upper() != token:
                # The token seems to be a word, but it might be a foreign word, a new word, it might contain
                # an unknown prefix/suffix... We will tag it as a common noun.
                tag = NOUN + COMMON + COMMON + INVARIABLE + "0000"
                token_tags = {self._tag_number_converter[tag]:
                              (1.0, token[:-1] if token[-1] == 's' else token)}
            else:
                # Apparently, it is not a word, neither a number. It might be a symbol.
                token_tags = {self._tag_number_converter[UNKNOWN]: (1.0, token)}
        return token_tags

    def choose_tags(self, possible_tags):
        """We get the possible tags that the tokens of a sentence can get, and choose the best ones.

        Using the syntactic table and the weightings for each token gotten from the lexicon, we are able to
        calculate the weighting of the whole sentence for each combination of tags. However, we don't simply
        inspect all the possible combinations and calculate their combined weightings, since there might be
        too many possible combinations. We divide the sentence in fragments and calculate the weighting for
        each one, and for their possible combinations, discarding all the possible combinations that we know
        beforehand that won't have the highest sentence weighting.

        :type possible_tags: list
        :param possible_tags: It is a list, where each element corresponds to a token in the sentence. This
        token is represented by a dict, where the keys are the (numerized) tags that the token might get, and
        the values are a tuple where the first element is the weighting and the second is the lemma.
        :rtype: tuple
        :return: A tuple containing a list of tags as its first element, and a list of lemmas as the second.
        """
        left_context, right_context = 2, 1  # Currently, the syntactic tag has this context.
        # We divide the sentence into fragments with a length of longest context (either the left or right).
        fragment_size = max(left_context, right_context)
        fragments = [possible_tags[fragment_order * fragment_size:(fragment_order + 1) * fragment_size]
                     for fragment_order in range((1 if len(possible_tags) % fragment_size else 0)
                                                 + int(len(possible_tags) / fragment_size))]
        fragment_number = len(fragments)
        # For each fragment, we calculate all the possible tag combinations.
        frags_combs = [list(product(*fragment)) for fragment in fragments]
        # As we process the fragments from rightmost to leftmost, we create a structure that contains, for
        # each tag combination of the current fragment, the tag combination for all the fragments already
        # processes that has the highest weighting. For the initial fragment, that value is simply no tag and
        # a value of 0.0 (the weighting values are shown as logarithms).
        post_frag_combs = {}
        # We process the fragments starting from the rightmost.
        for current_frag_order in range(fragment_number - 1, -1, -1):
            # We will use the current fragment (a list of dicts, each one representing a token in the sentence
            # with its possible values of tags and corresponding weightings) and the set of all the possible
            # tag combinations for this fragment.
            fragment = fragments[current_frag_order]
            current_frag_combs = frags_combs[current_frag_order]

            # We will also use the set of all possible combinations of tags belonging to the surrounding
            # fragments and that could be part of the context of any tag of the current fragment.
            prev_context = [tuple(t.keys()) for t in fragments[current_frag_order - 1][-left_context:]]\
                if current_frag_order > 0 else [(None, )] * left_context
            post_context = [tuple(t.keys()) for t in fragments[current_frag_order + 1][:right_context]]\
                if current_frag_order < fragment_number - 1 else [(None, )] * right_context
            context_combs = list(product(*(prev_context + post_context)))

            # For the current fragment, we will calculate which is the tag combination with highest weighting
            # (and its weighting) for each of the possible context tags combinations.
            combs_for_context = {}
            for context_comb in context_combs:
                # Given this tag combination for the current fragment context, we will calculate the tag
                # combination of the current fragment that maximizes the fragment weighting.
                # The weighting of a fragment is calculated as the multiplication of each tag weighting,
                # multiplied by each tag context weighting, and multiplied as well by the maximum weighting
                # for the compatible fragments at its right (calculated in the previous iteration of the
                # algorithm, or a 100% if the current fragment is the first to be processed).
                combs_for_current_frag_in_context = {}
                for current_frag_comb in current_frag_combs:
                    current_comb_weighting = 0.0  # It is the logarithm of 100%.
                    for current_tag_order, current_tag in enumerate(current_frag_comb):
                        context = \
                            (context_comb[:left_context]
                             + current_frag_comb
                             + context_comb[left_context:])[current_tag_order:
                                                            current_tag_order + left_context + right_context
                                                            + 1]
                        # In the syntactic table, the main key represent the tag whose context we calculated,
                        # followed by the tags for the left context in inverse order (first the nearest tag
                        # and last the furthest one), followed by the tags for the right context (again, first
                        # the nearest one and last the furthest one).
                        reordered_context = context[left_context::-1] + context[left_context + 1:]
                        # The default weighting is half the minimum weighting of the whole table. If we do not
                        # see the current combination in the table, this is the value that we will use.
                        context_weighting = -47.6245104413 - 0.301029995664
                        current_tag_weighting = log10(fragment[current_tag_order][current_tag][0])
                        # We search in the table for the current tag combination.
                        current_structure = self._syntactic_table
                        for order, tag in enumerate(reordered_context):
                            if tag in current_structure:
                                if order < len(reordered_context) - 1:
                                    # We are not yet at the end of the tree: get a level deeper and reiterate.
                                    current_structure = current_structure[tag]
                                else:
                                    # Already at a leave of the tree. We get the weighting.
                                    context_weighting = current_structure[tag]
                            else:
                                # The tag combination was not in the syntactic tag: it was never seen during
                                # the training.
                                break

                        # We calculate the multiplication of the context weighting and the current tag
                        # weighting.
                        current_comb_weighting += context_weighting + current_tag_weighting
                    # We already calculated the weighting for the current fragment combination in the current
                    # context, so we save it in the table.
                    combs_for_current_frag_in_context[current_frag_comb] = current_comb_weighting
                combs_for_context[context_comb] = combs_for_current_frag_in_context
            if current_frag_order == len(fragments) - 1:
                # This is the rightmost fragment, so it does not have fragments at its right. All done.
                post_frag_combs = combs_for_context
            else:
                # We have to "assemble" this fragment with the compatible tag combination of the fragments at
                # its right that has the highest weighting.
                combs_for_context_aux = {}
                # For each possible context for the current fragment...
                for context_tags, context_data in combs_for_context.items():
                    # ... we are going to try each possible current fragment tag combination...
                    for fragment_tags, weighting in context_data.items():
                        # ... and for them, we will check which are the context and fragment tag combinations
                        # for the fragment we processed in the previous iteration...
                        for post_context_tags, post_data in post_frag_combs.items():
                            # ... so we can check whether that combination is "assembleable" with the chosen
                            # context and tag combination for the current fragment.
                            if post_context_tags[:left_context] == fragment_tags[:left_context]:
                                # The context combination for previous fragment is compatible with the current
                                # fragment tag combination. We now check which tag combination for the
                                # previously processed fragment is compatible with the current fragment
                                # context combination.
                                for post_fragment_tags, post_weighting in post_data.items():
                                    if post_fragment_tags[:right_context] ==\
                                            context_tags[left_context:][:len(post_fragment_tags
                                                                             [:right_context])]:
                                        # It is compatible. If this is not the first compatible one that we
                                        # found, we will retain the one with highest weighting.
                                        combs_for_context_aux[context_tags] =\
                                            combs_for_context_aux.setdefault(context_tags, {})
                                        collision =\
                                            [(k, v)
                                             for k, v in combs_for_context_aux[context_tags].items()
                                             if k[:left_context] == fragment_tags[:left_context]]
                                        if collision:
                                            if collision[0][1] < weighting + post_weighting:
                                                del combs_for_context_aux[context_tags][collision[0][0]]
                                            else:
                                                continue
                                        combs_for_context_aux[context_tags][fragment_tags +
                                                                            post_fragment_tags] =\
                                            weighting + post_weighting
                post_frag_combs = combs_for_context_aux
        highest_weighting_numerized_tags, weighting = max([(tag_list, weighting)
                                                           for dictionary in post_frag_combs.values()
                                                           for tag_list, weighting in dictionary.items()],
                                                          key=lambda x: x[1])
        highest_weighting_tags = [self._tag_number_converter[tag] for tag in highest_weighting_numerized_tags]
        highest_weighting_lemmas = [possible_tags[o][t][1]
                                    for o, t in enumerate(highest_weighting_numerized_tags)]

        return highest_weighting_tags, highest_weighting_lemmas

    def get_unprefixed_form(self, token):
        """Tries to remove prefixes from the beginning of a word, so the resulting word is in the lexicon.

        :type token: str
        :param token: The token from which we want to take the prefixes away (in case it is a Spanish word).
        :rtype: str
        :return: The word form without the prefixes that might have been found.
        """
        if sub('[A-ZÑÁÉÍÓÚÜa-zñáéíóúü‒–−­—―-]+', '', token):
            # The token is not a Spanish word token.
            return token

        # We try to find a prefix at the beginning of the word.
        unprefixed_forms = []
        intermediate_forms = [token]
        form_order = 0
        while form_order < len(intermediate_forms):
            current_form = intermediate_forms[form_order]
            structure = self._prefixes
            while len(current_form) > 3:  # The lexeme must be at least 4 characters long.
                if current_form[0] in '-‒–−­—―':
                    # There might be a dash separating the prefix from the lexeme. We take it away.
                    current_form = current_form[1:]
                    continue
                if '' in structure:
                    # This means that the letters from the beginning of the word form a prefix.
                    # We take into account that adding a prefix might have effects in the lexeme such as
                    # doubling an "r" or forming an hiatus and thus adding a stress mark.
                    if current_form[0].lower() == 'r':
                        if current_form[1].lower() == 'r':
                            # The double "r" at the beginning of a word becomes a single "r".
                            current_form = current_form[1:]
                        else:
                            # There are no Spanish words that start with the phoneme written with a single "r"
                            # between vowels. The prefix should end in dash, "r", "l", "n" or "s".
                            if token[-len(current_form) - 1] not in '-‒–−­—―rlns':
                                break
                    if current_form in self._lexicon:
                        # After removing what seemed to be a prefix, the resulting word form is in the lexicon
                        if current_form not in unprefixed_forms:
                            unprefixed_forms.append(current_form)
                    # There might be a longer prefix or even more than one prefix. We continue searching.
                    if current_form not in intermediate_forms:
                        intermediate_forms.append(current_form)
                if current_form[0] in structure:
                    structure = structure[current_form[0]]
                    current_form = current_form[1:]
                else:
                    break
            form_order += 1
        if unprefixed_forms:
            # We return the longest possible prefixed lexeme found.
            token = unprefixed_forms[0]
        return token

    def start_with_lowercase(self, sentence_tokens):
        """Decides whether the first word in a sentence should be lowercased.

        :type sentence_tokens: list
        :param sentence_tokens: A list of tokens (each one being a str).
        :rtype: list
        :return: The same list of tokens, with the 1st word of the list lowercased if it is not a proper noun.
        """
        sentence = sentence_tokens[:]
        for token_order, token in enumerate(sentence):
            # We identify the first word of the list of tokens (there might be punctuation marks).
            if token not in self._lexicon or\
                    PUNCTUATION not in [self._tag_number_converter[tag][0]
                                        for tag in chain.from_iterable(self._lexicon[token].values())]:
                # This is the first word of the sentence. We will lowercase it if it has any uppercase
                # character (but not all of them)...
                if token != token.lower() and len(token) == 1 or token[1:] == token[1:].lower():
                    # ... if the next token is not a word with the first character in uppercase...
                    if token_order == len(sentence) - 1 or \
                            sentence[token_order + 1][0] == \
                            sentence[token_order + 1][0].lower():
                        # ... and if the lowercased form exists and is more common than the original version.
                        if token.lower() in self._form_count and\
                                (token not in self._form_count or
                                 2 * self._form_count[token] < self._form_count[token.lower()]):
                            sentence[token_order] = token.lower()
                            break
        return sentence

    def tag_text(self, text):
        """It takes the text, tokenizes it and set a morphosyntactic tag and a lemma to each one.

        The tokens are grouped into sentences.

        :type text: str
        :param text: The text to be tokenized and tagged.
        :rtype: list
        :return: A list where each item represents a sentence in the given text as a list of tuples. Each
        tuple represents a token of the sentence and contains the token itself, the part-of-speech tag and the
        lemma.
        """
        tokenized_sentences = Tokenizer.segmenta(text, separa_frases=True)
        results = []
        for sentence_order, sentence_tokens in enumerate(tokenized_sentences):
            # We extract all the possible tags corresponding to each form.
            tokens = self.start_with_lowercase(sentence_tokens)
            possible_sentence_tags =\
                [self.get_possible_tags(token, proper_nouns_are_lemmas=True)
                 for token in tokens]
            sentence_tags, sentence_lemmas = self.choose_tags(possible_sentence_tags)
            results.append(list(zip(sentence_tokens, sentence_tags, sentence_lemmas)))
        return results

    @staticmethod
    def test():
        """A simple test function to show how to use this package. Takes a text and prints the result.

        :rtype: None
        :return: None
        """
        text = 'Su estancia acabó bruscamente al comienzo de la primavera. ' \
               'De la noche a la mañana, el enano portavoz empezó a desarrollar un carácter esquinado. ' \
               'Le sorprendí hurgando en el botiquín y al verse emboscado, se desordenó el pelo y dijo que ' \
               'tenía hambre. Le enseñé la alacena. Cuando quisiera, podía coger lo que necesitara. ' \
               'Pero a la primera de cambio, en cuanto pensaba que nadie le vigilaba, volvía al baño a por ' \
               'paracetamol o píldoras contraceptivas. ' \
               'Daba golpes en la mesa con la mano abierta. ' \
               'Protegía con el brazo el plato de la comida, y se enojaba si yo trataba de poner al otro ' \
               'enano su propio plato. ' \
               'Se escondía detrás de las cortinas y se le oía reír con la voz de un conspirador. ' \
               'Nos dimos cuenta de que ya no cambiaban de estatura. ' \
               'El enano portavoz siempre tenía altura humana, y su semblante parecía el de un príncipe ' \
               'eslavo, iracundo y feliz de estar en el destierro. ' \
               'Cuando no era presa de sus cambios de humor, paseaba por el salón y en su camino elástico ' \
               'era como si pronto fueran a llegar noticias con el resultado de una batalla. ' \
               'Alguna vez, cuando estaba con mi marido en la cama, me sorprendí pensando en el enano ' \
               'principesco, con la mirada humedecida en todos los países de Europa, y me estremecía ' \
               'imaginando sus manos enlucidas sobre mi cara. ' \
               'El otro enano desmejoraba, se quedaba flaco y amarillo; no participaba de las ' \
               'conversaciones y sonreía débilmente cuando nos dirigíamos a él. ' \
               'Fue este enano el que un día se metió en la bañera mientras me duchaba. ' \
               'No chillé. Su cara inspiraba lástima, era completamente inocuo, y estaba tan demacrado y ' \
               'recortado que podría haberlo aplastado con el pie. ' \
               'Me pidió perdón, dándome la espalda. ' \
               'Había decidido abordarme en el baño porque sólo así podría hablarme fuera de la vigilancia ' \
               'del otro. ' \
               'Es esta vida que llevamos, dijo. ' \
               'No es culpa de nadie. ' \
               'Nosotros estamos habituados al exterior, al césped, a la lluvia sobre la cara. ' \
               'A que de vez en cuando nos cosan con yeso alguna grieta. ' \
               'Todo esto es nuevo para nosotros. ' \
               'Sólo queríamos cambiar de vida. ' \
               'Intentaron desanimarnos diciéndonos que otros lo habían intentado antes y habían fracasado. '\
               'Pensamos que sólo querían retenernos, pero tenían razón. ' \
               'Tenemos que irnos. ' \
               'No sé cuánto tiempo me llevará convencerle, pero tiene que pensar que lo hace por mí,' \
               'porque no entiende que está desquiciado.'
        tagger = SyntacticTagger()
        tags = tagger.tag_text(text)
        for sentence in tags:
            tokens_line, tags_line, lemmas_line = '|', '|', '|'
            for token, tag, lemma in sentence:
                max_length = max([len(token), len(tag), len(lemma)])
                tokens_line += token + (' ' * (max_length - len(token))) + '|'
                tags_line += tag + (' ' * (max_length - len(tag))) + '|'
                lemmas_line += lemma + (' ' * (max_length - len(lemma))) + '|'
            print('-' * len(tokens_line))
            print(tokens_line)
            print(tags_line)
            print(lemmas_line)
            print('-' * len(tokens_line))
            print()


if __name__ == "__main__":
    SyntacticTagger.test()
