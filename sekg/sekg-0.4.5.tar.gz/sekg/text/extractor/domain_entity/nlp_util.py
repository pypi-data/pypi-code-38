import re

import spacy


class SpacyNLPFactory:
    """

    """
    __domain_extractor_nlp=None
    __identifier_extractor_nlp=None
    @staticmethod
    def create_spacy_nlp_for_domain_extractor():
        """
        load a spacy nlp pipeline for extract domain entity and relations
        :return:
        """
        if SpacyNLPFactory.__domain_extractor_nlp is not  None:
            return SpacyNLPFactory.__domain_extractor_nlp

        # todo: fix this, write a class as Spacy Component
        nlp = spacy.load("en")
        id_re = re.compile(r"id|ID|Id")

        prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
        nlp.tokenizer = spacy.tokenizer.Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                                  infix_finditer=infix_re.finditer,
                                                  suffix_search=suffix_re.search, token_match=id_re.match)

        SpacyNLPFactory.__domain_extractor_nlp=nlp
        return nlp

    @staticmethod
    def create_spacy_nlp_for_identifier_extractor():
        """
        load a spacy nlp pipeline for extract domain entity and relations
        :return:
        """
        if SpacyNLPFactory.__identifier_extractor_nlp is not None:
            return SpacyNLPFactory.__identifier_extractor_nlp

        # todo: fix this, write a class as Spacy Component
        nlp = spacy.load("en")
        hyphen_re = re.compile(r"[A-Za-z\d]+-[A-Za-z\d]+|'[a-z]+|''")

        prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
        infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
        nlp.tokenizer = spacy.tokenizer.Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                                  infix_finditer=infix_re.finditer,
                                                  suffix_search=suffix_re.search, token_match=hyphen_re.match)

        SpacyNLPFactory.__identifier_extractor_nlp=nlp
        return nlp
