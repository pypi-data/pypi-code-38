import re

import spacy


class SpacyNLPFactory:
    """

    """
    __domain_extractor_nlp = None
    __identifier_extractor_nlp = None
    __simple_nlp = None

    @classmethod
    def create_spacy_nlp_for_domain_extractor(clss):
        """
        load a spacy nlp pipeline for extract domain entity and relations
        :return:
        """
        if clss.__domain_extractor_nlp is not None:
            return clss.__domain_extractor_nlp

        # todo: fix this, write a class as Spacy Component
        nlp = spacy.load("en")
        id_re = re.compile(r"id|ID|Id")

        prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
        nlp.tokenizer = spacy.tokenizer.Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                                  infix_finditer=infix_re.finditer,
                                                  suffix_search=suffix_re.search, token_match=id_re.match)

        clss.__domain_extractor_nlp = nlp
        return nlp

    @classmethod
    def create_spacy_nlp_for_identifier_extractor(clss):
        """
        load a spacy nlp pipeline for extract domain entity and relations
        :return:
        """
        if clss.__identifier_extractor_nlp is not None:
            return clss.__identifier_extractor_nlp

        # todo: fix this, write a class as Spacy Component
        nlp = spacy.load("en")
        hyphen_re = re.compile(r"[A-Za-z\d]+-[A-Za-z\d]+|'[a-z]+|''")

        prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
        nlp.tokenizer = spacy.tokenizer.Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                                  infix_finditer=infix_re.finditer,
                                                  suffix_search=suffix_re.search, token_match=hyphen_re.match)

        clss.__identifier_extractor_nlp = nlp
        return nlp

    @classmethod
    def create_simple_nlp_pipeline(clss):
        """
        create a simple nlp pipeline, without NER and dependency parser, could tokenize and pos,lemma, will be very fast.        :return:
        """
        if clss.__simple_nlp is not None:
            return clss.__simple_nlp

        NLP = spacy.load('en', disable=["ner", "parser"])
        hyphen_re = re.compile(r"[A-Za-z\d]+-[A-Za-z\d]+|'[a-z]+|''")
        prefix_re = spacy.util.compile_prefix_regex(NLP.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(NLP.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(NLP.Defaults.suffixes)
        NLP.tokenizer = spacy.tokenizer.Tokenizer(NLP.vocab, prefix_search=prefix_re.search,
                                                  infix_finditer=infix_re.finditer,
                                                  suffix_search=suffix_re.search, token_match=hyphen_re.match)

        clss.__simple_nlp = NLP
        return NLP
