# -*- coding: utf-8 -*-
""" Process/Core functions for Named Entities Recognition.
"""
from nazca.utils.tokenizer import RichStringTokenizer


###############################################################################
# NER PROCESS #################################################################
###############################################################################
class NerProcess(object):
    """ High-level process for Named Entities Recognition
    """

    def __init__(self, ner_sources, preprocessors=None,
                 filters=None, unique=False):
        """ Initialise the class.

        :tokenizer: an instance of tokenizer
        """
        self.ner_sources = list(ner_sources)
        self.preprocessors = preprocessors or []
        self.filters = filters or []
        self.unique = unique

    def add_ner_source(self, process):
        """ Add a ner process
        """
        self.ner_sources.append(process)

    def add_preprocessors(self, preprocessor):
        """ Add a preprocessor
        """
        self.preprocessors.append(preprocessor)

    def add_filters(self, filter):
        """ Add a filter
        """
        self.filters.append(filter)

    def process_text(self, text):
        """ High level function for analyzing a text
        """
        tokenizer = RichStringTokenizer(text)
        return self.recognize_tokens(tokenizer)

    def recognize_tokens(self, tokens):
        """ Recognize Named Entities from a tokenizer or
        an iterator yielding tokens.
        """
        last_stop = 0
        named_entities = []
        for token in tokens:
            if token.start < last_stop:
                continue  # this token overlaps with a previous match
            # Applies preprocessors
            # XXX Preprocessors may be sources dependant
            for preprocessor in self.preprocessors:
                token = preprocessor(token)
                if not token:
                    break
            if not token:
                continue
            recognized = False
            for process in self.ner_sources:
                for uri in process.recognize_token(token):
                    named_entities.append((uri, process.name, token))
                    recognized = True
                    last_stop = token.end
                    if self.unique:
                        break
                if recognized and self.unique:
                    break
        # XXX Postprocess/filters may be sources dependant
        return self.postprocess(named_entities)

    def postprocess(self, named_entities):
        """ Postprocess the results by applying filters """
        for filter in self.filters:
            named_entities = filter(named_entities)
        return named_entities
