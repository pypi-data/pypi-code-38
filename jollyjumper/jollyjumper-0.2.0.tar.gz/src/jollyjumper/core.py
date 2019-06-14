#!/usr/bin/python
# Rules are based on previous work from Pablo Ruiz
# https://github.com/postdataproject/skas-archived/blob/devel/skas/phonmet/syll/grapheme2syllable.py
from .pipeline import load_pipeline
from .rules import rules


def get_enjambment(text):
    """
    Scan a text for all possible enjambment types.
    :param text: String with the original poem
    :return: Dictionary of all enjambment types and their lines of occurrence
    """
    enjambment_types = ['sirrematic', 'sirrematic_relation_words_preposition',
                        'sirrematic_relation_words_conjunction',
                        'sirrematic_relation_words_determiners',
                        'sirrematic_orational', 'relation_words_verbs',
                        'sirrematic_with_verb', 'link',
                        'sirrematic_prepositional_without_de',
                        'sirrematic_prepositional',
                        'sirrematic_prepositional_before_noun_adjective']
    enjambments = {}
    nlp = load_pipeline()
    doc = nlp(text)
    for token in doc:
        # We look for tmesis before any other enjambment type because the text
        # has to be preprocessed
        if token._.has_tmesis:  # noqa
            enjambments[token._.line] = {"type": 'tmesis', "on": token.text.split('-\n')}  # noqa
            continue
        # Last token cannot be the beginning of an enjambment
        # (unless it's tmesis)
        if token == doc[-1]:
            continue
        previous_token = doc[token.i - 1]
        next_token = doc[token.i + 1]
        # We look for enjambment when if there are words
        # before and after a newline character
        if token.text == '\n' and not previous_token.is_punct and not next_token.is_punct:
            for enjambment_type in enjambment_types:
                enjambment_func = rules.get(f'get_{enjambment_type}_enjambment',
                                            lambda *_: None)
                enjambment = enjambment_func(previous_token, next_token)
                if enjambment:
                    enjambments[token._.line] = {"type": enjambment_type, "on": enjambment}  # noqa
                    break
    return enjambments
